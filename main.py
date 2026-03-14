import asyncio
import uuid

from langchain.messages import HumanMessage

from local_agent.a2a.connected_agents import A2AConnection
from local_agent.agent import call_conversation_agent


async def start(conversation_id: str):
    a2a_connection: A2AConnection = A2AConnection()
    remote_agents: dict = await a2a_connection.get_agents()

    while True:
        user_input: str = input("User message: ")
        message: dict = await call_conversation_agent(messages=[HumanMessage(user_input)], remote_agents=remote_agents, conversation_id=conversation_id)
        print("AI Message:", message["messages"][-1].content)

if __name__ == "__main__":
    conversation_id: str = str(uuid.uuid4())
    asyncio.run(start(conversation_id))