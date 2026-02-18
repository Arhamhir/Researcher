from app.services.embeddings import get_embedding
from app.services.retrieval import search_similar_sections

SIMILARITY_THRESHOLD = 0.80


def novelty_node(state: dict) -> dict:
    print("[NOVELTY] Starting...")
    sections = state.get("paper_sections", {})
    paper_id = str(state.get("paper_id", "")).strip()  # Current paper ID to exclude self

    text_for_novelty = (
        sections.get("abstract", "") + "\n" +
        sections.get("introduction", "")
    ).strip()

    if not text_for_novelty:
        return {
            "novelty_review": {
                "score": 0,
                "similarity_max": 1.0,
                "issues": ["No abstract or introduction found for novelty analysis."],
                "suggestions": ["Ensure the paper includes an abstract and introduction."]
            }
        }

    query_embedding = get_embedding(text_for_novelty)
    results = search_similar_sections(
        query_embedding,
        top_k=10,
        exclude_paper_id=paper_id if paper_id else None
    )

    if paper_id:
        normalized_pid = paper_id.lower()
        results = [r for r in results if str(r.get("paper_id", "")).strip().lower() != normalized_pid]
    
    # If no other papers in database, give high novelty score
    if not results:
        print("[NOVELTY] No existing papers to compare against - high novelty")
        return {
            "novelty_review": {
                "score": 9,
                "similarity_max": 0.0,
                "issues": [],
                "suggestions": [
                    "First paper in the system - novelty cannot be compared.",
                    "Consider adding more context about the state of the field."
                ]
            }
        }
    
    max_similarity = max([r["similarity"] for r in results], default=0.0)

    if max_similarity > SIMILARITY_THRESHOLD:
        score = 3
        issues = [
            f"High similarity ({max_similarity:.2f}) with existing academic work."
        ]
        suggestions = [
            "Clearly articulate how this work differs from existing literature.",
            "Emphasize unique contributions or novel methodology."
        ]
    else:
        score = 8
        issues = []
        suggestions = [
            "Highlight the novelty explicitly in the introduction.",
            "Compare contributions clearly against prior work."
        ]

    print(f"[NOVELTY] Completed with score: {score}, max_similarity: {max_similarity:.2f}")

    return {
        "novelty_review": {
            "score": score,
            "similarity_max": round(max_similarity, 2),
            "issues": issues,
            "suggestions": suggestions
        }
    }
