import json
import os
from typing import Any, Dict, List, Optional

from openai import OpenAI


ISSUE_LABELS = [
    "cleanliness", "noise", "check-in", "location", "comfort", "value",
    "staff/service", "communication", "amenities", "other"
]


def get_client_from_secrets(st) -> OpenAI:
    # παίρνει το key από Streamlit Secrets ή env var
    api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    if not api_key:
        st.error('Λείπει OPENAI_API_KEY στα Secrets. (Manage app → Settings → Secrets)')
        st.stop()
    return OpenAI(api_key=api_key)


def call_json(client: OpenAI, model: str, temperature: float, system: str, user: str) -> Dict[str, Any]:
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)


def detect_language(client: OpenAI, model: str, text: str) -> str:
    data = call_json(
        client=client,
        model=model,
        temperature=0.0,
        system="Return JSON only.",
        user=f"""Detect the language of this text. Return JSON:
{{"language": "English" or "Greek" or "Mixed"}}.

TEXT:
{text}"""
    )
    return data.get("language", "English")


def analyze_review(client: OpenAI, model: str, text: str) -> Dict[str, Any]:
    data = call_json(
        client=client,
        model=model,
        temperature=0.2,
        system="You are a strict JSON generator. Output valid JSON only.",
        user=f"""
Analyze the review and return JSON with this schema:
{{
  "summary": "1-2 sentences",
  "sentiment": "positive" | "mixed" | "negative",
  "issues": [
    {{"label": one of {ISSUE_LABELS}, "severity": 1-5, "note": "short"}}
  ],
  "highlights": ["short bullet", "short bullet"]
}}

Review:
{text}
"""
    )
    data.setdefault("issues", [])
    data.setdefault("highlights", [])
    data.setdefault("summary", "")
    data.setdefault("sentiment", "mixed")
    return data


def length_rules(length: str) -> str:
    if length == "Short":
        return "Keep it very short: 2–4 lines max."
    if length == "Premium":
        return "Write a premium reply: 10–14 lines, still concise, elegant."
    return "Keep it concise: 5–8 lines."


def build_reply_prompt(
    platform: str,
    tone: str,
    language: str,
    length: str,
    analysis: Dict[str, Any],
    review_text: str,
    property_profile: Optional[Dict[str, Any]] = None,
) -> str:
    issues = analysis.get("issues", [])
    sentiment = analysis.get("sentiment", "mixed")
    summary = analysis.get("summary", "")
    highlights = analysis.get("highlights", [])

    prop_block = ""
    if property_profile:
        prop_block = f"""
Property profile (context):
- Name: {property_profile.get("name","")}
- Location: {property_profile.get("location","")}
- Description: {property_profile.get("description","")}
- Check-in: {property_profile.get("checkin","")}
- Check-out: {property_profile.get("checkout","")}
- Amenities: {property_profile.get("amenities","")}
- House rules: {property_profile.get("house_rules","")}
""".strip()

    crisis_mode = ""
    # Auto crisis mode when negative OR serious issues
    severe = any(int(i.get("severity", 3)) >= 4 for i in issues)
    if sentiment == "negative" or severe:
        crisis_mode = """
Crisis mode ON:
- Apologize once.
- Acknowledge concern without admitting liability.
- Mention one concrete corrective action.
- Keep it calm, professional, reputation-protective.
""".strip()

    return f"""
You are a professional short-term rental host assistant.

Platform: {platform}
Tone: {tone}
Language: {language}

Guest review (raw):
{review_text}

Analysis:
- Sentiment: {sentiment}
- Summary: {summary}
- Highlights: {highlights}
- Issues: {issues}

{prop_block}

Rules:
- {length_rules(length)}
- Be warm and professional.
- If issues exist: apologize once, mention a realistic corrective action, invite them back.
- Avoid overpromising, refunds, or admissions of liability.
- Output ONLY the final reply text (no headings, no bullets).

{crisis_mode}
""".strip()


def generate_text(client: OpenAI, model: str, temperature: float, prompt: str) -> str:
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()
