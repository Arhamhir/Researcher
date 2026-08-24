from app.services.llm_client import get_json_response, normalize_review

SYSTEM_PROMPT = """
You are an academic peer reviewer specializing in research methodology.

Evaluate ONLY the methodology of the paper.

Rules:
- Be balanced and evidence-based
- Do not evaluate novelty or writing quality
- Penalize missing experimental detail, missing baselines, and weak evaluation design
- Allow partial credit when methodology is described but lacks depth
- Output MUST be valid JSON
- Output NOTHING except JSON

Scoring rubric:
- 9-10: rigorous, reproducible, strong experimental controls
- 7-8: good methodology with minor gaps
- 5-6: moderate weaknesses but usable methodology
- 3-4: serious weaknesses that threaten validity
- 0-2: fundamentally weak or non-reproducible methodology

JSON schema:
{
  "score": number (0 to 10),
  "issues": list of strings,
  "suggestions": list of strings
}
"""


def methodology_node(state: dict) -> dict:
    print("[METHODOLOGY] Starting...")
    methodology_text = state.get("paper_sections", {}).get("methodology", "")

    if not methodology_text.strip():
        return {
            "methodology_review": {
                "score": 0.0,
                "issues": ["Methodology section missing or empty."],
                "suggestions": ["Include a clear methodology section."]
            }
        }

    methodology_excerpt = methodology_text[:9000]
    prompt = f"{SYSTEM_PROMPT}\n\nMethodology section (excerpt):\n{methodology_excerpt}"

    response = get_json_response(prompt)

    if "error" in response:
        # An API/infra failure (rate limit, timeout, bad key) says nothing
        # about the paper's actual methodology - it is not evidence of a
        # "fundamentally weak" method. Scoring it 0 would incorrectly trip
        # the critic's hard-reject threshold for what could be a strong
        # paper. Fall back to a neutral, content-aware heuristic instead so
        # infrastructure hiccups can't manufacture a false rejection.
        word_count = len(methodology_text.split())
        has_signal = any(
            keyword in methodology_text.lower()
            for keyword in ("baseline", "dataset", "evaluat", "experiment", "metric")
        )
        score = 6.0 if (word_count >= 150 and has_signal) else 5.0
        parsed = {
            "score": score,
            "issues": [
                f"Automated methodology review failed ({response.get('error', 'unknown error')}); "
                "a neutral heuristic score was used instead of a full assessment."
            ],
            "suggestions": ["Re-run the review once the underlying API issue clears for a full assessment."]
        }
    else:
        parsed = normalize_review(response)

    print(f"[METHODOLOGY] Completed with score: {parsed.get('score')}")
    return {"methodology_review": parsed}
