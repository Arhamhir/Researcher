import json
import re
from app.services.llm_client import get_json_response

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


def _extract_json(text: str) -> dict:
    """Extract the first JSON object from text safely."""
    try:
        return json.loads(text)
    except Exception:
        # Strip code fences if present
        cleaned = re.sub(r"^```(json)?|```$", "", text.strip())
        # Find first {...} block
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return {
            "score": 0.0,
            "issues": ["Invalid JSON from model."],
            "suggestions": ["Ensure strict JSON-only responses or check API key."]
        }


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

    try:
        response = get_json_response(prompt, system_prompt=None)
        
        if "error" in response:
            parsed = {
                "score": 0.0,
                "issues": [f"LLM call failed: {response.get('error', 'Unknown error')}"],
                "suggestions": ["Ensure the AZURE_OPENAI_API_KEY and endpoint are set and valid."]
            }
        else:
            parsed = response
    except Exception as e:
        parsed = {
            "score": 0.0,
            "issues": [f"LLM call failed: {str(e)}"],
            "suggestions": ["Ensure the AZURE_OPENAI_API_KEY and endpoint are set and valid."]
        }

    print(f"[METHODOLOGY] Completed with score: {parsed.get('score')}")
    return {"methodology_review": parsed}
