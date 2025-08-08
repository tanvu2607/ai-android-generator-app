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
- `LLM_PROVIDER` (optional): set to `gemini` to use Google Gemini.
- `GEMINI_API_KEY` (optional): required if `LLM_PROVIDER=gemini`.

### Use Gemini locally (Docker)
```bash
docker run -p 8000:8000 \
  -e LLM_PROVIDER=gemini \
  -e GEMINI_API_KEY=YOUR_GEMINI_KEY \
  ai-android-generator
```

### Use Gemini in GitHub Actions (web only)
1) Trên GitHub (repo của bạn) mở: Settings → Secrets and variables → Actions → New repository secret
2) Name: `GEMINI_API_KEY`, Value: dán key của bạn → Add secret
3) Actions workflow sẽ tự dùng Gemini nếu secret tồn tại (không cần thêm gì khác)

## API
- POST `/generate` (multipart/form-data):
  - `app_name`, `package_name`, `min_sdk`, `target_sdk`, `description?`, `prompt`
  - Response: `application/zip` attachment.