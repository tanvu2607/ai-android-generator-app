from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes.generate import router as generate_router

app = FastAPI(title="AI Android Generator App", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static directory (optional for future assets)
app.mount("/static", StaticFiles(directory="backend/app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(_: Request) -> str:
    return (
        """
        <!doctype html>
        <html>
        <head>
            <meta charset=\"utf-8\" />
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
            <title>AI Android Generator</title>
            <style>
              body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 24px; color: #111; }
              .container { max-width: 860px; margin: 0 auto; }
              input, textarea, select, button { font-size: 16px; }
              label { font-weight: 600; }
              .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
              .row { margin-bottom: 12px; }
              textarea { width: 100%; height: 140px; }
              input[type=number] { width: 120px; }
              .actions { display: flex; gap: 12px; }
              .card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
              .muted { color: #6b7280; font-size: 14px; }
              .title { font-size: 22px; font-weight: 700; margin-bottom: 8px; }
            </style>
        </head>
        <body>
          <div class=\"container\">
            <h1>AI Android Generator</h1>
            <p class=\"muted\">Tạo bộ khung ứng dụng Android (Gradle + Jetpack Compose) từ yêu cầu tiếng Việt/English. Có thể dùng OpenAI nếu đặt biến môi trường <code>OPENAI_API_KEY</code>.</p>

            <form id=\"form\" method=\"post\" action=\"/generate\">
              <div class=\"card\">
                <div class=\"title\">Cấu hình dự án</div>
                <div class=\"grid\">
                  <div class=\"row\">
                    <label>Tên ứng dụng</label><br />
                    <input type=\"text\" name=\"app_name\" value=\"AIAndroidApp\" required />
                  </div>
                  <div class=\"row\">
                    <label>Package name</label><br />
                    <input type=\"text\" name=\"package_name\" value=\"com.example.aiandroidapp\" required />
                  </div>
                </div>
                <div class=\"grid\">
                  <div class=\"row\">
                    <label>Min SDK</label><br />
                    <input type=\"number\" name=\"min_sdk\" value=\"24\" />
                  </div>
                  <div class=\"row\">
                    <label>Target SDK</label><br />
                    <input type=\"number\" name=\"target_sdk\" value=\"34\" />
                  </div>
                </div>
                <div class=\"row\">
                  <label>Mô tả ngắn</label><br />
                  <input type=\"text\" name=\"description\" placeholder=\"Ứng dụng demo sinh giao diện bằng AI\" />
                </div>
              </div>

              <div class=\"card\" style=\"margin-top: 12px\"> 
                <div class=\"title\">Yêu cầu / Prompt</div>
                <div class=\"row\">
                  <textarea name=\"prompt\" placeholder=\"Ví dụ: Tạo app ToDo với màn hình danh sách, thêm/sửa/xoá, thanh tìm kiếm, dùng Jetpack Compose\" required></textarea>
                </div>
              </div>

              <div class=\"actions\" style=\"margin-top: 12px\">
                <button type=\"submit\">Sinh dự án và tải về (.zip)</button>
              </div>
            </form>

            <script>
              const form = document.getElementById('form');
              form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const fd = new FormData(form);
                const res = await fetch('/generate', { method: 'POST', body: fd });
                if (!res.ok) { alert('Lỗi sinh dự án'); return; }
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url; a.download = 'android-project.zip';
                document.body.appendChild(a); a.click(); a.remove();
                URL.revokeObjectURL(url);
              });
            </script>
          </div>
        </body>
        </html>
        """
    )

app.include_router(generate_router)