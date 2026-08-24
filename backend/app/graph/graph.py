from langgraph.graph import StateGraph, START, END

from app.graph.state import GraphState
from app.graph.nodes.methodology_node import methodology_node
from app.graph.nodes.novelty_node import novelty_node
from app.graph.nodes.citation_node import citation_node
from app.graph.nodes.clarity_node import clarity_node
from app.graph.nodes.final_decision_node import final_decision_node

def build_graph():
    """Build the review graph.

    Flow:
    START -> [methodology, novelty, citation, clarity] (parallel)
          -> critic/final_decision
          -> END
    """
    print("[GRAPH] Building graph...")
    graph = StateGraph(GraphState)

    # Add all review nodes
    graph.add_node("methodology", methodology_node)
    graph.add_node("novelty", novelty_node)
    graph.add_node("citation", citation_node)
    graph.add_node("clarity", clarity_node)
    graph.add_node("critic", final_decision_node)

    # Fan-out from START to all review nodes in parallel
    graph.add_edge(START, "methodology")
    graph.add_edge(START, "novelty")
    graph.add_edge(START, "citation")
    graph.add_edge(START, "clarity")

    # Barrier join: critic executes only after ALL review nodes complete
    graph.add_edge(["methodology", "novelty", "citation", "clarity"], "critic")

    # Final judgment ends the graph
    graph.add_edge("critic", END)

    print("[GRAPH] Graph compiled successfully")
    return graph.compile()
