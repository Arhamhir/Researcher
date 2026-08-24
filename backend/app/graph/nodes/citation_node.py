import re

from app.services.llm_client import get_json_response, normalize_review

SYSTEM_PROMPT = """
You are an academic peer reviewer focused ONLY on citation quality and literature grounding.

Evaluate using these standards, applied proportionately - a paper can ground its
claims in prior work without a separately labeled "Related Work" section (e.g.
citations woven directly into the introduction and discussion):
- Prior work coverage breadth
- Correctness and relevance of citation context
- Presence of recent work (last 3-5 years), where the field moves quickly
- Whether claims are supported by references

Be fair and evidence-based. Most competently-written papers belong in the 5-8
range; reserve scores below 3 for papers that make substantive claims with
essentially no citation support at all.

Scoring policy:
- 9-10: comprehensive, current, and well-integrated citations
- 7-8: good but with some gaps
- 5-6: adequate citation support with clear room for improvement
- 3-4: sparse or dated citation support
- 0-2: claims made with no meaningful citation support

Return ONLY valid JSON:
{
  "score": number,
  "issues": [string],
  "suggestions": [string]
}
"""

# Inline citation markers (e.g. "[3]", "[4, 7]", "(Smith et al., 2021)") that
# show a paper is citing prior work even when section parsing didn't manage
# to isolate a dedicated "related work" or "references" section - common with
# two-column PDF layouts where headers get mangled during text extraction.
_CITATION_MARKER = re.compile(
    r"\[\d+(?:\s*,\s*\d+)*\]|\([A-Z][\w'-]+(?:\s+et al\.?)?,?\s*\d{4}\)|\bet al\.?\b"
)


def _has_inline_citations(text: str) -> bool:
    return bool(_CITATION_MARKER.search(text or ""))


def citation_node(state: dict) -> dict:
    print("[CITATION] Starting...")
    sections = state.get("paper_sections", {})
    full_text = state.get("paper_text", "") or sections.get("full_text", "")

    related_work = sections.get("related_work", "")
    introduction = sections.get("introduction", "")
    references = sections.get("references", "")

    has_dedicated_sections = any([related_work.strip(), references.strip()])
    has_inline_citations = _has_inline_citations(full_text) or _has_inline_citations(introduction)

    if not has_dedicated_sections and not has_inline_citations:
        return {
            "citation_review": {
                "score": 2,
                "issues": ["No related-work section, references, or in-text citation markers detected."],
                "suggestions": [
                    "Add a dedicated related-work section and references list.",
                    "Support major claims with explicit citations."
                ]
            }
        }

    if has_dedicated_sections:
        payload = (
            f"Introduction (excerpt):\n{introduction[:3000]}\n\n"
            f"Related Work (excerpt):\n{related_work[:6000]}\n\n"
            f"References (excerpt):\n{references[:4000]}"
        )
    else:
        # Citations exist (inline markers found) but weren't captured under a
        # labeled section - give the model the fuller body text instead of
        # penalizing the paper for a section-detection miss.
        payload = (
            "No dedicated related-work/references section was detected, but "
            "in-text citation markers were found - judge citation quality "
            "from the body text directly.\n\n"
            f"Full paper text (excerpt):\n{full_text[:9000]}"
        )

    response = get_json_response(f"{SYSTEM_PROMPT}\n\nPaper text:\n{payload}")
    if isinstance(response, dict) and "error" not in response:
        return {"citation_review": normalize_review(response)}

    # LLM call failed - fall back to a heuristic seeded from what we already
    # know (dedicated sections vs. inline-only) rather than a flat guess.
    issues = ["Automated citation review failed; fallback heuristic applied."]
    suggestions = ["Verify references include foundational and recent work."]
    score = 6 if has_dedicated_sections else 5

    if not related_work.strip():
        issues.append("No dedicated related-work narrative found.")
        score -= 1
    if "202" not in (related_work + references + full_text)[:20000]:
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
