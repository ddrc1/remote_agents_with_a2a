import uuid

from a2a.types import Message, Part, Role, TaskStatusUpdateEvent, TextPart, AgentCard
from a2a.client.client import Client

from langchain.tools import ToolRuntime, tool

@tool
async def send_remote_message(runtime: ToolRuntime, agent_name: str, message: str):
    """
    This tool allows sending a message to the chosen agent.

    Args:
        agent_name (str): Name of the chosen agent
        message (str): Message to be answered by the agent

    Returns:
        str: Message returned from the agent
    """
    context: dict = runtime.context
    context_id: str | None = context.get("conversation_id")
    remote_agents: dict = context.get("remote_agents", {})

    if agent_name not in remote_agents:
        return f"Agent {agent_name} not found"
    
    client: Client = remote_agents[agent_name]["client"]
    card: AgentCard = remote_agents[agent_name]["card"]
    message_id: str = str(uuid.uuid4())

    payload: Message = Message(
        role=Role.user, 
        message_id=message_id,
        context_id=context_id,
        parts=[Part(root=TextPart(text=message))]
    )

    response_items: list[Message] = []
    try:
        if card.capabilities.streaming:
            async for task, update in client.send_message(payload):
                if isinstance(update, TaskStatusUpdateEvent) and update.status.message:
                    message = update.status.message
                    response_items.append(message)
        else:
            async for item in client.send_message(payload):
                response_items.append(item)

    except Exception as e:
        ValueError(f"Failed to get response from agent {agent_name}: {str(e)}")

    if not response_items:
        ValueError(f"No response received from agent {agent_name}")

    final_message = response_items[-1]
    if not isinstance(final_message, Message):
        ValueError(f"Unexpected response type from agent {agent_name}")

    text_parts = []
    for part in final_message.parts:
        if hasattr(part, "root") and isinstance(part.root, TextPart):
            text_parts.append(part.root.text)

    if not text_parts:
        ValueError(f"No text content in response from agent {agent_name}")

    return "".join(text_parts)