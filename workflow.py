from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

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


NODE_SEQUENCE = [
    "Observation",
    "Defect Analysis",
    "Classification",
    "Missing Information Detection",
    "Confidence Calculation",
    "Human Review Gate",
    "Final Triage Output",
]


def _observe_defect(defect: Dict[str, Any]) -> Dict[str, Any]:
    text = " ".join(
        [
            str(defect.get("bug_description", "")),
            str(defect.get("logs", "")),
            str(defect.get("screenshot_notes", "")),
            str(defect.get("additional_comments", "")),
        ]
    ).strip()
    return {
        "raw_text": text,
        "bug_description": defect.get("bug_description", ""),
        "logs": defect.get("logs", ""),
        "screenshot_notes": defect.get("screenshot_notes", ""),
        "additional_comments": defect.get("additional_comments", ""),
    }


def _analyze_defect(observation: Dict[str, Any]) -> Dict[str, Any]:
    text = observation["raw_text"].lower()
    if "checkout" in text:
        problem_summary = "Checkout flow defect"
    elif "auth" in text or "login" in text:
        problem_summary = "Authentication defect"
    elif "payment" in text:
        problem_summary = "Payment processing defect"
    elif "api" in text:
        problem_summary = "API integration defect"
    else:
        problem_summary = "General product defect"

    return {"problem_summary": problem_summary, "signal_keywords": sorted(set(re.findall(r"[a-z]+", text)))[:10]}


def _classify_defect(analysis: Dict[str, Any], defect: Dict[str, Any]) -> Dict[str, Any]:
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

    return {
        "severity": severity,
        "priority": priority,
        "module_impact": module,
        "suggested_owner": owner,
        "analysis_summary": analysis["problem_summary"],
    }


def _detect_missing_information(defect: Dict[str, Any]) -> List[str]:
    missing = []
    if not defect.get("logs"):
        missing.append("runtime logs")
    if not defect.get("screenshot_notes"):
        missing.append("screenshot notes")
    if not defect.get("additional_comments"):
        missing.append("additional customer context")
    return missing


def _calculate_confidence(analysis: Dict[str, Any], severity: str, missing: List[str]) -> float:
    confidence = 0.72
    if severity == "critical":
        confidence = 0.82
    elif severity == "high":
        confidence = 0.78
    elif severity == "medium":
        confidence = 0.74
    elif severity == "low":
        confidence = 0.68

    if analysis["problem_summary"] != "General product defect":
        confidence += 0.04
    if not missing:
        confidence += 0.04
    else:
        confidence -= 0.05 * min(len(missing), 3)

    return round(max(0.0, min(1.0, confidence)), 2)


def _review_gate(severity: str, missing: List[str], confidence: float) -> bool:
    return bool(missing) or severity in {"critical", "high"} or confidence < 0.75


def _agentic_triage(defect: Dict[str, Any]) -> DefectTriageResult:
    observation = _observe_defect(defect)
    analysis = _analyze_defect(observation)
    classification = _classify_defect(analysis, defect)
    missing = _detect_missing_information(defect)
    confidence = _calculate_confidence(analysis, classification["severity"], missing)
    needs_human_review = _review_gate(classification["severity"], missing, confidence)

    return DefectTriageResult(
        severity=classification["severity"],
        priority=classification["priority"],
        module_impact=classification["module_impact"],
        suggested_owner=classification["suggested_owner"],
        missing_information=missing,
        confidence_score=confidence,
        needs_human_review=needs_human_review,
        execution_sequence=NODE_SEQUENCE,
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

    agentic_result = _agentic_triage(defect_input.to_dict())

    prompt = build_triage_prompt(defect_input.to_dict())
    if client is None:
        client = OllamaClient()

    response_text = client.generate(prompt)
    payload = _parse_json_response(response_text)

    if payload:
        try:
            result = DefectTriageResult.from_dict(payload)
            result.execution_sequence = NODE_SEQUENCE
            return result.to_dict()
        except Exception:
            pass

    return agentic_result.to_dict()
