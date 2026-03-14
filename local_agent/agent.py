from datetime import datetime
from typing import TypedDict
from dotenv import load_dotenv
import json
import os

from langchain.agents import create_agent
from langchain.messages import HumanMessage, AIMessage, AnyMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.state import CompiledStateGraph

from local_agent.tools.send_remote_message import send_remote_message
from local_agent.prompt import CONVERSATION_PROMPT

load_dotenv(dotenv_path="math_agent/.env")

GEMINI_DEFAULT_MODEL = os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.5-flash")


class Context(TypedDict):
    remote_agents: dict
    conversation_id: str


__agent: CompiledStateGraph = create_agent(
    model=ChatGoogleGenerativeAI(model=GEMINI_DEFAULT_MODEL),
    context_schema=Context,
    tools=[send_remote_message]
)


async def call_conversation_agent(messages: list[AnyMessage], remote_agents: dict, conversation_id: str) -> str:
    if not messages or not isinstance(messages[-1], HumanMessage):
        return ""
    
    user_message: HumanMessage = messages[-1]
    current_date: str = datetime.now().strftime("%Y-%m-%d")

    prompt_template: ChatPromptTemplate = ChatPromptTemplate(
        [
            SystemMessagePromptTemplate.from_template(template=CONVERSATION_PROMPT),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=user_message.content)
        ]
    )

    remote_agents_description: list[dict] = "\n".join(
        [json.dumps({
        "name": remote_agent["card"].name,
        "description": remote_agent["card"].description,
        "skills": [{"name": skill.name,
            "description": skill.description,
            "exemples": ";".join(skill.examples),
            "tags": ",".join(skill.tags)
            } for skill in remote_agent["card"].skills]
        }) for remote_agent in remote_agents.values()])

    formated_prompt: list[AnyMessage] = prompt_template.format_messages(
        messages=messages,
        remote_agents=remote_agents_description,
        current_date=current_date
    )

    response: dict = await __agent.ainvoke(
        input={"messages": formated_prompt},
        context={"remote_agents": remote_agents, "conversation_id": conversation_id}
    )
    message: AIMessage = response["messages"][-1]
    
    return {"messages": [message]}


