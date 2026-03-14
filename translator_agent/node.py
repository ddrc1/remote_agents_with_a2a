from datetime import datetime
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.messages import HumanMessage, AIMessage, AnyMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import MessagesState

from langgraph.graph.state import CompiledStateGraph

from .prompt import TRANSLATOR_PROMPT

load_dotenv(dotenv_path="math_agent/.env")


__agent: CompiledStateGraph = create_agent(
    model=ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite"),
    tools=[]
)

def call_translator_agent(state: MessagesState) -> MessagesState:
    messages: list[AnyMessage] = state.get("messages", [])
    if not messages or not isinstance(messages[-1], HumanMessage):
        return ""
    
    user_message: HumanMessage = messages[-1]
    current_date: str = datetime.now().strftime("%Y-%m-%d")

    prompt_template: ChatPromptTemplate = ChatPromptTemplate(
        [
            SystemMessagePromptTemplate.from_template(template=TRANSLATOR_PROMPT),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=user_message.content)
        ]
    )

    formated_prompt: list[AnyMessage] = prompt_template.format_messages(
        messages=messages, 
        current_date=current_date
    )

    response: dict = __agent.invoke(input={"messages": formated_prompt})
    message: AIMessage = response["messages"][-1]
    
    return {"messages": [message]}


