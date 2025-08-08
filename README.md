# ai-android-generator-app
Ứng dụng Android AI Generator - tạo ứng dụng Android bằng AI.

## Cấu trúc
- `backend/`: FastAPI server + bộ template Android (Gradle + Jetpack Compose)
- `scripts/dev.sh`: Script chạy nhanh (tự tạo venv nếu có thể), cài deps, chạy test, khởi chạy server
- `Dockerfile`: Chạy backend bằng Docker

## Chạy nhanh
- Docker

```bash
docker build -t ai-android-generator .
docker run -p 8000:8000 -e OPENAI_API_KEY=$OPENAI_API_KEY ai-android-generator
```

- Hoặc chạy trực tiếp (nếu môi trường cho phép tạo venv):

```bash
bash scripts/dev.sh
```

Mở `http://localhost:8000` để nhập prompt, server trả về file `android-project.zip`.

## Chọn LLM: Gemini (khuyên dùng khi không có OpenAI)
- Dùng trên GitHub Actions (chỉ cần web/điện thoại):
  - Vào repo trên GitHub → Settings → Secrets and variables → Actions → New repository secret
  - Name: `GEMINI_API_KEY`
  - Value: dán key của bạn → Add secret
  - Workflow sẽ tự dùng Gemini khi secret tồn tại (không cần chỉnh gì thêm)

- Dùng khi chạy Docker cục bộ:
```bash
docker run -p 8000:8000 \
  -e LLM_PROVIDER=gemini \
  -e GEMINI_API_KEY=YOUR_GEMINI_KEY \
  ai-android-generator
```

## Ghi chú
- Có thể đặt `OPENAI_API_KEY` để sinh Compose UI từ OpenAI; nếu không có, hệ thống dùng `GEMINI_API_KEY` (nếu `LLM_PROVIDER=gemini`), hoặc fallback.
