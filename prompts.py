from __future__ import annotations


def build_triage_prompt(defect: dict) -> str:
    return f"""
You are a defect triage assistant. Analyze the defect details and return a JSON object with the following fields:
- severity: one of critical, high, medium, low
- priority: one of p0, p1, p2, p3
- module_impact: a short module or service name
- suggested_owner: a concise owner/team name
- missing_information: an array of missing details that should be collected before closing the defect
- confidence_score: a float between 0.0 and 1.0
- needs_human_review: boolean

Use the defect evidence carefully and prioritize actionable, concise output.

Defect details:
Bug Description: {defect.get('bug_description', '')}
Logs: {defect.get('logs', '')}
Screenshot Notes: {defect.get('screenshot_notes', '')}
Additional Comments: {defect.get('additional_comments', '')}

Return ONLY valid JSON.
"""
