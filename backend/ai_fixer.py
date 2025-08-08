import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse
import httpx
import re
import time

TEMPLATES_ROOT = Path("backend/app/templates/android")

SYSTEM_MSG = (
    "You are a senior Android/Gradle engineer. You will receive: (1) a Kotlin/Gradle build error log, "
    "and (2) current template files used to generate an Android app. "
    "Your job is to propose minimal edits to the template files so that future generated projects build successfully.\n\n"
    "Rules:\n"
    "- Only edit files under backend/app/templates/android/**.\n"
    "- Prefer adding missing imports, dependencies, or adjusting MainActivity template.\n"
    "- Output STRICT JSON with key 'edits': a list of { 'path': string, 'new_content': string }. Paths are repository-relative.\n"
    "- Do not include explanations outside JSON."
)

ALLOWED_COMPOSE_COMPILER_VERSION = "1.5.14"


def call_gemini(api_key: str, prompt: str) -> str:
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "generationConfig": {"temperature": 0.1},
    }
    backoffs = [2, 5, 10, 20]
    for i, delay_s in enumerate(backoffs + [0]):  # final try without extra delay index
        try:
            with httpx.Client(timeout=60) as client:
                r = client.post(url, json=payload)
                if r.status_code == 429:
                    raise httpx.HTTPStatusError("rate limit", request=r.request, response=r)
                r.raise_for_status()
                data = r.json()
                candidates = data.get("candidates") or []
                if not candidates:
                    return "{}"
                parts = ((candidates[0].get("content") or {}).get("parts") or [])
                if not parts:
                    return "{}"
                return parts[0].get("text", "{}")
        except httpx.HTTPStatusError as e:
            if getattr(e.response, "status_code", None) == 429 and i < len(backoffs):
                time.sleep(delay_s)
                continue
            raise
        except httpx.RequestError:
            if i < len(backoffs):
                time.sleep(delay_s)
                continue
            raise
    return "{}"


def gather_template_snapshot() -> str:
    lines: List[str] = []
    for p in sorted(TEMPLATES_ROOT.rglob("*.j2")):
        rel = p.as_posix()
        content = p.read_text(encoding="utf-8")
        lines.append(f"===== FILE: {rel} =====\n{content}\n")
    return "\n".join(lines)


def sanitize_gradle_content(path: Path, content: str) -> str:
    if path.as_posix().endswith("app/build.gradle.kts.j2"):
        # Force a known-good Compose compiler extension version
        content = re.sub(
            r'(kotlinCompilerExtensionVersion\s*=\s*")([^"]+)(")',
            rf'\g<1>{ALLOWED_COMPOSE_COMPILER_VERSION}\3',
            content,
        )
    return content


def apply_edits(edits: List[Dict[str, Any]]) -> int:
    applied = 0
    for edit in edits:
        path = Path(edit.get("path", ""))
        new_content = edit.get("new_content", None)
        if not path or new_content is None:
            continue
        if not path.as_posix().startswith("backend/app/templates/android/"):
            # Only allow edits inside templates
            continue
        target = Path(path.as_posix())
        target.parent.mkdir(parents=True, exist_ok=True)
        sanitized = sanitize_gradle_content(target, new_content)
        target.write_text(sanitized, encoding="utf-8")
        applied += 1
    return applied


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True, help="Path to generated project directory")
    parser.add_argument("--log", required=True, help="Path to build log file")
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        print("[ai-fixer] GEMINI_API_KEY not set; skipping", file=sys.stderr)
        return 0

    log_text = Path(args.log).read_text(encoding="utf-8") if Path(args.log).exists() else ""
    snapshot = gather_template_snapshot()

    user_prompt = (
        f"Build error log below. Propose minimal template fixes as JSON per rules.\n\n"
        f"===== BUILD LOG =====\n{log_text}\n\n"
        f"===== TEMPLATE SNAPSHOT (truncated allowed) =====\n{snapshot}\n"
    )

    raw = call_gemini(api_key, SYSTEM_MSG + "\n\n" + user_prompt)
    # Extract JSON block if wrapped in fences
    text = raw.strip()
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1]
        text = text.replace("json", "", 1).strip()
    try:
        data = json.loads(text or "{}")
    except Exception:
        print("[ai-fixer] Failed to parse JSON from model", file=sys.stderr)
        return 0

    edits = data.get("edits") or []
    applied = apply_edits(edits)
    print(f"[ai-fixer] Applied {applied} edit(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())