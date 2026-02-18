"""LLM client utility for Azure OpenAI integration."""
import json
import re
from openai import AzureOpenAI, NotFoundError
from app.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_CHAT_API_VERSION,
    AZURE_OPENAI_CHAT_DEPLOYMENT,
)


def _get_client(api_version: str) -> AzureOpenAI:
    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=api_version,
    )


def _candidate_api_versions() -> list[str]:
    versions = [
        AZURE_OPENAI_CHAT_API_VERSION,
        "2024-10-21",
        "2024-02-01",
    ]
    deduped = []
    for version in versions:
        if version and version not in deduped:
            deduped.append(version)
    return deduped


def extract_json_response(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    try:
        return json.loads(text)
    except Exception:
        # Strip markdown code fences
        cleaned = re.sub(r"^```(json)?|```$", "", text.strip())
        # Find first {...} block
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return None


def call_llm(prompt: str, system_prompt: str = None, max_tokens: int = 1500) -> dict:
    """
    Call Azure OpenAI LLM with given prompt.
    
    Args:
        prompt: User message
        system_prompt: System message (optional)
        max_tokens: Max tokens in response
        
    Returns:
        Dictionary with 'success' (bool) and 'content' (str) or 'error' (str)
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    deployment = (AZURE_OPENAI_CHAT_DEPLOYMENT or "").strip()
    last_error = None

    for api_version in _candidate_api_versions():
        try:
            client = _get_client(api_version)
            response = client.chat.completions.create(
                model=deployment,
                messages=messages,
                temperature=0.7,
                max_tokens=max_tokens
            )

            return {
                "success": True,
                "content": response.choices[0].message.content
            }
        except NotFoundError as e:
            last_error = e
            continue
        except Exception as e:
            last_error = e
            break

    tried = ", ".join(_candidate_api_versions())
    return {
        "success": False,
        "error": (
            f"Azure chat failed for deployment '{deployment}' at endpoint '{AZURE_OPENAI_ENDPOINT}'. "
            f"Tried API versions: {tried}. Original error: {last_error}"
        ),
    }


def get_json_response(prompt: str, system_prompt: str = None, max_tokens: int = 1500) -> dict:
    """
    Call LLM and extract JSON from response.
    
    Returns parsed JSON dict on success, or error dict on failure.
    """
    result = call_llm(prompt, system_prompt, max_tokens)
    
    if not result["success"]:
        return {
            "error": result["error"],
            "fallback": True
        }
    
    json_data = extract_json_response(result["content"])
    if json_data is None:
        return {
            "error": "Failed to extract JSON from response",
            "raw_response": result["content"],
            "fallback": True
        }
    
    return json_data
