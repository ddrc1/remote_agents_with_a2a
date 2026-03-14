from typing import AsyncIterable

from langchain_core.runnables import RunnableConfig
from langchain.messages import AIMessage

from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import Message, Part, TaskState, TextPart
from a2a.utils import new_agent_text_message, new_agent_parts_message

from .graph import compiled_graph

class TranslatorAgent():
    def invoke(self, user_message: str, context_id: str) -> str:
        config: RunnableConfig = {"configurable": {"thread_id": context_id}}
        result: dict = compiled_graph.invoke({"messages": [{"role": "user", "content": user_message}]}, config)
        message: AIMessage = result["messages"][-1]
        
        return message.content
    
    async def stream(self, user_message: str, context_id: str) -> AsyncIterable[tuple[str, bool]]:
        config: RunnableConfig = {"configurable": {"thread_id": context_id}}
        is_last_part: bool = False
        async for event in compiled_graph.astream_events(input={"messages": [{"role": "user", "content": user_message}]}, stream_mode="values", config=config):
            content: str = ""
            event_type: str = event.get("event")
            event_name: str = event.get("name")
            is_end_of_chain: bool = event_type == "on_chain_end"
            is_langgraph_event: bool = event_name == "LangGraph"

            if is_end_of_chain and is_langgraph_event:
                current_output: dict | list[dict] = event["data"]["output"]
                is_last_part = True
                content = current_output["messages"][-1].content
            else:
                content = event_type
            
            yield content, is_last_part


class TranslatorAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent: TranslatorAgent = TranslatorAgent()
    
    async def execute(self, request_context: RequestContext, event_queue: EventQueue):
        context_id: str | None = request_context.context_id
        task_id: str | None = request_context.task_id
        message: Message | None = request_context.message
        user_input: str = request_context.get_user_input()
        
        if not task_id or not context_id:
            raise ValueError("RequestContext must have task_id and context_id")
        if not message:
            raise ValueError("RequestContext must have a message")
        
        updater = TaskUpdater(event_queue, request_context.task_id, context_id)
        if not request_context.current_task:
            await updater.submit()
        await updater.start_work()

        async for item in self.agent.stream(user_message=user_input, context_id=context_id):
            content, is_last_part = item
            parts: list[Part] = [Part(root=TextPart(text=content))]
            if not is_last_part:
                await updater.update_status(
                    state=TaskState.working,
                    message=updater.new_agent_message(parts),
                )
            else:
                await updater.complete(message=updater.new_agent_message(parts))

        # result: str = self.agent.invoke(user_message=request_context.get_user_input(), context_id=request_context.context_id)        


    async def cancel(self, context, event_queue):
        raise NotImplementedError("Cancellation is not implemented for MathAgent")
    
