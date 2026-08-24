"""LLM client for Groq's OpenAI-compatible chat completions API.

Groq exposes chat (and audio) completions only - there is no embeddings
endpoint - and is reached with the standard `openai` SDK by pointing it at
Groq's base_url. Structured JSON output is enforced with Groq's native JSON
Schema "strict" mode (constrained decoding, 100% schema adherence) on the
models that support it, falling back to best-effort JSON Object Mode for any
other model so a misconfigured GROQ_MODEL degrades instead of hard-failing.
"""
import json
import re
import time

from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    RateLimitError,
)

from app.core.config import (
    GROQ_API_KEY,
    GROQ_API_BASE,
    GROQ_MODEL,
    GROQ_REASONING_EFFORT,
)

# Confirmed by Groq's docs to support strict JSON Schema structured outputs.
STRICT_SCHEMA_MODELS = {"openai/gpt-oss-20b", "openai/gpt-oss-120b"}

# All four review agents emit the same shape, so one schema covers them.
REVIEW_SCHEMA = {
    "name": "peer_review",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "score": {"type": "number"},
            "issues": {"type": "array", "items": {"type": "string"}},
            "suggestions": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["score", "issues", "suggestions"],
        "additionalProperties": False,
    },
}

MAX_RETRIES = 2

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is not set.")
        _client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_API_BASE)
    return _client


def _response_format(model: str) -> dict:
    if model in STRICT_SCHEMA_MODELS:
        return {"type": "json_schema", "json_schema": REVIEW_SCHEMA}
    return {"type": "json_object"}


def _extra_params(model: str) -> dict:
    """gpt-oss reasoning controls; harmless no-op for other models."""
    if model.startswith("openai/gpt-oss"):
        return {
            "reasoning_effort": GROQ_REASONING_EFFORT,
            # Keep chain-of-thought out of message.content so it never
            # collides with the JSON answer we need to parse.
            "reasoning_format": "hidden",
        }
    return {}


def _retry_after_seconds(error) -> float:
    try:
        return float(error.response.headers.get("retry-after", ""))
    except Exception:
        return 0.0


def extract_json_response(text: str):
    """Extract JSON from LLM response, handling markdown code fences or stray text."""
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        cleaned = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE)
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return None


def call_llm(prompt: str, system_prompt: str = None, max_tokens: int = 1500) -> dict:
    """
    Call Groq's chat completions API.

    Returns {"success": True, "content": str} on success, or
    {"success": False, "error": str} on failure (auth, rate limit exhausted,
    malformed request, network/server errors, or an empty/truncated response).
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    model = (GROQ_MODEL or "").strip()
    response_format = _response_format(model)
    budget = max_tokens

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            client = _get_client()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                max_completion_tokens=budget,
                response_format=response_format,
                **_extra_params(model),
            )
            content = response.choices[0].message.content
            if not content or not content.strip():
                # Most often the reasoning phase consumed the whole token
                # budget before the model could emit its JSON answer. Give
                # it more room once before giving up.
                last_error = RuntimeError(
                    "Model returned an empty response "
                    f"(finish_reason={response.choices[0].finish_reason})."
                )
                if attempt < MAX_RETRIES:
                    budget = int(budget * 1.75)
                    continue
                break

            return {"success": True, "content": content}

        except AuthenticationError as e:
            # Retrying a bad/missing key never helps.
            return {
                "success": False,
                "error": f"Groq authentication failed - check GROQ_API_KEY. ({e})",
            }

        except BadRequestError as e:
            last_error = e
            # A strict schema request can be rejected outright (e.g. GROQ_MODEL
            # was overridden to one that doesn't support it). Degrade once.
            if response_format.get("type") == "json_schema":
                response_format = {"type": "json_object"}
                continue
            break

        except RateLimitError as e:
            last_error = e
            if attempt < MAX_RETRIES:
                wait = _retry_after_seconds(e) or (2 ** attempt)
                time.sleep(min(wait, 15))
                continue
            break

        except (APIConnectionError, APITimeoutError, InternalServerError) as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(1 + attempt)
                continue
            break

        except Exception as e:
            last_error = e
            break

    return {
        "success": False,
        "error": f"Groq chat completion failed for model '{model}': {last_error}",
    }


def get_json_response(prompt: str, system_prompt: str = None, max_tokens: int = 1500) -> dict:
    """
    Call the LLM and parse its JSON content.

    Returns the parsed dict on success, or {"error": ..., "fallback": True}
    so callers can apply a deterministic fallback instead of crashing.
    """
    result = call_llm(prompt, system_prompt, max_tokens)

    if not result["success"]:
        return {"error": result["error"], "fallback": True}

    parsed = extract_json_response(result["content"])
    if parsed is None:
        return {
            "error": "Failed to extract JSON from response",
            "raw_response": result["content"],
            "fallback": True,
        }

    return parsed


def normalize_review(data, max_items: int = 6) -> dict:
    """
    Coerce a parsed agent response into a well-formed review shape so a
    malformed or partially-correct model response never breaks the critic
    stage or the UI downstream.
    """
    if not isinstance(data, dict):
        data = {}

    try:
        score = float(data.get("score", 0))
    except (TypeError, ValueError):
        score = 0.0
    score = max(0.0, min(10.0, score))

    def _string_list(value):
        if not isinstance(value, list):
            return []
        return [
            str(item) for item in value
            if item is not None and str(item).strip()
        ][:max_items]

    return {
        "score": round(score, 1),
        "issues": _string_list(data.get("issues")),
        "suggestions": _string_list(data.get("suggestions")),
    }
