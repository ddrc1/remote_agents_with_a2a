from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.state import CompiledStateGraph

from .node import call_translator_agent

graph: StateGraph = StateGraph(MessagesState)

graph.add_node(node="translator_agent", action=call_translator_agent)

graph.add_edge(start_key=START, end_key="translator_agent")
graph.add_edge(start_key="translator_agent", end_key=END)

compiled_graph: CompiledStateGraph = graph.compile()