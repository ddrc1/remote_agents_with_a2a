from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.state import CompiledStateGraph

from .node import call_math_agent

graph: StateGraph = StateGraph(MessagesState)

graph.add_node(node="math_agent", action=call_math_agent)

graph.add_edge(start_key=START, end_key="math_agent")
graph.add_edge(start_key="math_agent", end_key=END)

compiled_graph: CompiledStateGraph = graph.compile()