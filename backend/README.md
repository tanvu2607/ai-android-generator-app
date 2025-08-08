# Backend - AI Android Generator App

## Quickstart

- Run locally (auto venv if available):

```bash
bash scripts/dev.sh
```

- Or with Docker:

```bash
docker build -t ai-android-generator .
docker run -p 8000:8000 -e OPENAI_API_KEY=$OPENAI_API_KEY ai-android-generator
```

Open http(s)://localhost:8000 to use the form. POST `/generate` returns a `.zip`.

## Environment
- `OPENAI_API_KEY` (optional): enable LLM UI generation; otherwise fallback layout is used.

## API
- POST `/generate` (multipart/form-data):
  - `app_name`, `package_name`, `min_sdk`, `target_sdk`, `description?`, `prompt`
  - Response: `application/zip` attachment.