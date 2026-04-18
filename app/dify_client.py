from __future__ import annotations

import json
from typing import Any

import requests


class DifyAPIError(RuntimeError):
    """Raised when a Dify API call fails or returns an unexpected payload."""


def _extract_analysis_text(response_json: dict[str, Any]) -> str:
    data = response_json.get("data", {})

    outputs = data.get("outputs")
    if isinstance(outputs, dict):
        for key in ("analysis", "result", "answer", "text", "output"):
            value = outputs.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    text_like_fields = (
        data.get("text"),
        data.get("answer"),
        response_json.get("answer"),
    )
    for value in text_like_fields:
        if isinstance(value, str) and value.strip():
            return value.strip()

    # Fall back to rendering structured outputs so the user still gets useful data.
    if isinstance(outputs, dict) and outputs:
        return json.dumps(outputs, indent=2, ensure_ascii=True)

    raise DifyAPIError("Dify returned no readable analysis text in the response payload.")


def run_workflow(
    *,
    api_key: str,
    base_url: str,
    user_id: str,
    inputs: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """Run a Dify workflow in blocking mode and return extracted analysis + full payload."""

    url = f"{base_url.rstrip('/')}/workflows/run"
    payload = {
        "inputs": inputs,
        "response_mode": "blocking",
        "user": user_id,
    }

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
    except requests.RequestException as exc:
        raise DifyAPIError(f"Could not reach Dify API: {exc}") from exc

    if response.status_code >= 400:
        detail = response.text.strip() or "No error details returned."
        raise DifyAPIError(
            f"Dify API returned {response.status_code}: {detail}"
        )

    try:
        response_json = response.json()
    except ValueError as exc:
        raise DifyAPIError("Dify API response was not valid JSON.") from exc

    analysis_text = _extract_analysis_text(response_json)
    return analysis_text, response_json
