# ai-android-generator-app
Ứng dụng Android AI Generator - tạo ứng dụng Android bằng AI.

## Cấu trúc
- `backend/`: FastAPI server + bộ template Android (Gradle + Jetpack Compose)
- `scripts/dev.sh`: Script chạy nhanh (tự tạo venv nếu có thể), cài deps, chạy test, khởi chạy server
- `Dockerfile`: Chạy backend bằng Docker

## Chạy nhanh
- Ưu tiên: Docker

```bash
docker build -t ai-android-generator .
docker run -p 8000:8000 -e OPENAI_API_KEY=$OPENAI_API_KEY ai-android-generator
```

- Hoặc chạy trực tiếp (nếu môi trường cho phép tạo venv):

```bash
bash scripts/dev.sh
```

Mở `http://localhost:8000` để nhập prompt, server trả về file `android-project.zip`.

## Ghi chú
- Có thể đặt `OPENAI_API_KEY` để sinh Compose UI từ LLM; nếu không có, hệ thống dùng fallback UI.
