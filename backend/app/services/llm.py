import os
from typing import Optional
import re
import json

import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto").lower()

SYSTEM_PROMPT = (
    "You are an expert Android developer using Jetpack Compose. "
    "Given a user prompt, you output ONLY the Kotlin code for a Composable function body (inside setContent) "
    "that renders the requested UI. Avoid imports, package lines, and avoid the @Composable declaration itself."
)

FALLBACK_TEMPLATE = (
    "Column(modifier = Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {\n" \
    "  Text(\"%s\", style = MaterialTheme.typography.headlineMedium)\n" \
    "  Text(\"This screen was generated without external LLM (fallback).\", style = MaterialTheme.typography.bodyMedium)\n" \
    "  Button(onClick = { /* TODO */ }) { Text(\"Action\") }\n" \
    "}"
)


def _strip_code_fences(text: str) -> str:
    if "```" in text:
        # Remove markdown fences and optional language tag
        text = re.sub(r"```[a-zA-Z]*\n", "", text)
        text = text.replace("```", "")
    return text.strip()


async def _call_openai(prompt: str) -> str:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    content = resp.choices[0].message.content or ""
    return _strip_code_fences(content)


async def _call_gemini(prompt: str) -> str:
    # Gemini 2.5 Flash via Google Generative Language API v1beta
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": f"{SYSTEM_PROMPT}\n\nUser prompt:\n{prompt}"}
                ],
            }
        ],
        "generationConfig": {"temperature": 0.3},
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        # Expected: candidates[0].content.parts[0].text
        candidates = data.get("candidates") or []
        if candidates:
            parts = ((candidates[0].get("content") or {}).get("parts") or [])
            if parts and "text" in parts[0]:
                return _strip_code_fences(parts[0]["text"])
        # Fallback to empty
        return ""


async def generate_compose_content_from_prompt(prompt: str) -> str:
    # Provider selection
    provider = LLM_PROVIDER
    if provider == "auto":
        provider = "gemini" if GEMINI_API_KEY else ("openai" if OPENAI_API_KEY else "fallback")

    try:
        if provider == "gemini" and GEMINI_API_KEY:
            content = await _call_gemini(prompt)
            if content:
                return content
        if provider == "openai" and OPENAI_API_KEY:
            return await _call_openai(prompt)
    except Exception:
        pass

    # Fallback simple UI
    safe_title = prompt[:80].replace("\n", " ")
    return FALLBACK_TEMPLATE % safe_title