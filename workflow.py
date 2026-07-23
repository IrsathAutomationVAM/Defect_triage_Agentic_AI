from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Optional

import requests

from prompts import build_triage_prompt
from schemas import DefectInput, DefectTriageResult


class OllamaClient:
    def __init__(self, model: str = "qwen2:7b", base_url: Optional[str] = None) -> None:
        self.model = model
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
            return payload.get("response", "")
        except Exception:
            return ""


def _fallback_triage(defect: Dict[str, Any]) -> DefectTriageResult:
    text = " ".join(
        [
            str(defect.get("bug_description", "")),
            str(defect.get("logs", "")),
            str(defect.get("screenshot_notes", "")),
            str(defect.get("additional_comments", "")),
        ]
    ).lower()

    severity = "medium"
    if any(keyword in text for keyword in ["critical", "outage", "data loss", "security"]):
        severity = "critical"
    elif any(keyword in text for keyword in ["fail", "error", "exception", "unable"]):
        severity = "high"

    priority = "p2"
    if severity == "critical":
        priority = "p0"
    elif severity == "high":
        priority = "p1"

    module = "unknown"
    if "checkout" in text:
        module = "checkout"
    elif "auth" in text or "login" in text:
        module = "authentication"
    elif "payment" in text:
        module = "payments"
    elif "api" in text:
        module = "api"

    owner = "platform team"
    if module in {"checkout", "payments"}:
        owner = "payments team"
    elif module == "authentication":
        owner = "identity team"

    missing = []
    if not defect.get("logs"):
        missing.append("runtime logs")
    if not defect.get("screenshot_notes"):
        missing.append("screenshot notes")
    if not defect.get("additional_comments"):
        missing.append("additional customer context")

    return DefectTriageResult(
        severity=severity,
        priority=priority,
        module_impact=module,
        suggested_owner=owner,
        missing_information=missing,
        confidence_score=0.78 if not missing else 0.7,
        needs_human_review=bool(missing) or severity in {"critical", "high"},
    )


def _parse_json_response(response_text: str) -> Dict[str, Any]:
    match = re.search(r"\{.*\}", response_text, re.S)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}
    return {}


def triage_defect(defect: Any, client: Optional[OllamaClient] = None) -> Dict[str, Any]:
    if isinstance(defect, dict):
        defect_input = DefectInput.from_dict(defect)
    else:
        defect_input = defect

    prompt = build_triage_prompt(defect_input.to_dict())
    if client is None:
        client = OllamaClient()

    response_text = client.generate(prompt)
    payload = _parse_json_response(response_text)

    if payload:
        try:
            result = DefectTriageResult.from_dict(payload)
            return result.to_dict()
        except Exception:
            pass

    fallback = _fallback_triage(defect_input.to_dict())
    return fallback.to_dict()
