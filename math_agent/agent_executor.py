from langchain_core.runnables import RunnableConfig
from langchain.messages import AIMessage

from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message

from .graph import compiled_graph

class MathAgent():

    def invoke(self, user_message: str, context_id: str) -> str:
        config: RunnableConfig = {"configurable": {"thread_id": context_id}}
        result: dict = compiled_graph.invoke({"messages": [{"role": "user", "content": user_message}]}, config)
        message: AIMessage = result["messages"][-1]
        
        return message.content


class MathAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent: MathAgent = MathAgent()
    
    async def execute(self, request_context: RequestContext, event_queue: EventQueue):
        if not request_context.task_id or not request_context.context_id:
            raise ValueError("RequestContext must have task_id and context_id")
        if not request_context.message:
            raise ValueError("RequestContext must have a message")
        
        print(request_context.context_id)
        result: str = self.agent.invoke(user_message=request_context.get_user_input(), context_id=request_context.context_id)        

        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context, event_queue):
        raise NotImplementedError("Cancellation is not implemented for MathAgent")
    
