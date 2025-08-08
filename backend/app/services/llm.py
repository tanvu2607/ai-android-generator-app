import os
from typing import Optional

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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

async def generate_compose_content_from_prompt(prompt: str) -> str:
    if not OPENAI_API_KEY:
        # Fallback simple UI when no key provided
        safe_title = prompt[:80].replace("\n", " ")
        return FALLBACK_TEMPLATE % safe_title

    try:
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
        # Be defensive: extract inside code fences if present
        if "```" in content:
            parts = content.split("```")
            if len(parts) >= 3:
                content = parts[1 if parts[1].strip().startswith("kotlin") else 1].replace("kotlin", "", 1)
        return content.strip()
    except Exception:
        safe_title = prompt[:80].replace("\n", " ")
        return FALLBACK_TEMPLATE % safe_title