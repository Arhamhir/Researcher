from app.services.llm_client import get_json_response

SYSTEM_PROMPT = """
You are a strict peer reviewer focused ONLY on citation quality and literature grounding.

Evaluate using these standards:
- Prior work coverage breadth
- Correctness and relevance of citation context
- Presence of recent work (last 3-5 years)
- Whether claims are supported by references

Scoring policy:
- 9-10: comprehensive, current, and well-integrated citations
- 7-8: good but with some gaps
- 4-6: moderate weaknesses, missing important references
- 0-3: poor or largely absent citation support

Return ONLY valid JSON:
{
  "score": number,
  "issues": [string],
  "suggestions": [string]
}
"""


def citation_node(state: dict) -> dict:
    print("[CITATION] Starting...")
    sections = state.get("paper_sections", {})

    related_work = sections.get("related_work", "")
    introduction = sections.get("introduction", "")
    references = sections.get("references", "")

    if not any([related_work.strip(), references.strip()]):
        return {
            "citation_review": {
                "score": 1,
                "issues": ["No related-work or references content detected."],
                "suggestions": [
                    "Add a dedicated related-work section and references list.",
                    "Support major claims with explicit citations."
                ]
            }
        }

    payload = (
        f"Introduction (excerpt):\n{introduction[:3000]}\n\n"
        f"Related Work (excerpt):\n{related_work[:6000]}\n\n"
        f"References (excerpt):\n{references[:4000]}"
    )

    response = get_json_response(f"{SYSTEM_PROMPT}\n\nPaper text:\n{payload}")
    if isinstance(response, dict) and "error" not in response:
        score = max(0, min(10, float(response.get("score", 0))))
        return {
            "citation_review": {
                "score": round(score, 1),
                "issues": response.get("issues", [])[:6],
                "suggestions": response.get("suggestions", [])[:6],
            }
        }

    issues = ["Automated citation review failed; fallback heuristic applied."]
    suggestions = ["Verify references include foundational and recent work."]
    score = 5

    if not related_work.strip():
        issues.append("No dedicated related-work narrative found.")
        score -= 2
    if "202" not in (related_work + references):
        issues.append("No clearly recent citations detected.")
        score -= 1

    print(f"[CITATION] Completed with score: {max(1, score)}")
    return {
        "citation_review": {
            "score": max(1, score),
            "issues": issues,
            "suggestions": suggestions,
        }
    }
