from typing import TypedDict, Dict, Any

class GraphState(TypedDict, total=False):
    paper_id: str
    paper_sections: Dict[str, str]
    methodology_review: Any
    novelty_review: Any
    citation_review: Any
    clarity_review: Any
    final_decision: Any
    critic: Any
    retries: int
