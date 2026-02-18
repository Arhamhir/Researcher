from app.services.llm_client import get_json_response

SYSTEM_PROMPT = """
You are a strict academic writing reviewer focused ONLY on clarity and structure.

Evaluate:
- Logical flow from problem to contribution
- Precision and readability of language
- Whether claims are understandable and not vague
- Section coherence (abstract, intro, methods, results, conclusion)

Scoring policy:
- 9-10: clear, coherent, publication-ready writing
- 7-8: mostly clear with minor clarity defects
- 4-6: important clarity issues that hurt comprehension
- 0-3: confusing, fragmented, or highly ambiguous writing

Return ONLY valid JSON:
{
  "score": number,
  "issues": [string],
  "suggestions": [string]
}
"""


def clarity_node(state: dict) -> dict:
    print("[CLARITY] Starting...")
    sections = state.get("paper_sections", {})

    abstract = sections.get("abstract", "")
    introduction = sections.get("introduction", "")
    methodology = sections.get("methodology", "")
    results = sections.get("results", "")
    conclusion = sections.get("conclusion", "")

    payload = (
        f"Abstract:\n{abstract[:2500]}\n\n"
        f"Introduction:\n{introduction[:3500]}\n\n"
        f"Methodology:\n{methodology[:3500]}\n\n"
        f"Results:\n{results[:3500]}\n\n"
        f"Conclusion:\n{conclusion[:2500]}"
    )

    response = get_json_response(f"{SYSTEM_PROMPT}\n\nPaper text:\n{payload}")
    if isinstance(response, dict) and "error" not in response:
        score = max(0, min(10, float(response.get("score", 0))))
        return {
            "clarity_review": {
                "score": round(score, 1),
                "issues": response.get("issues", [])[:6],
                "suggestions": response.get("suggestions", [])[:6],
            }
        }

    issues = []
    suggestions = []
    if len(abstract.split()) < 60:
        issues.append("Abstract is too short to communicate full contribution.")
        suggestions.append("Expand abstract with objective, method, and key findings.")
    if not conclusion.strip():
        issues.append("Conclusion section is missing.")
        suggestions.append("Add a conclusion with limitations and future work.")
    if len(introduction.split()) < 120:
        issues.append("Introduction lacks sufficient context and motivation.")
        suggestions.append("Strengthen problem framing and contribution statement.")

    score = max(1, 10 - 2 * len(issues))
    print(f"[CLARITY] Completed with score: {score}")
    return {
        "clarity_review": {
            "score": score,
            "issues": issues,
            "suggestions": suggestions,
        }
    }
