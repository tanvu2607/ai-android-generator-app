import asyncio
import os
import gradio as gr

from backend.app.services.generator import AndroidProjectConfig, generate_android_project_zip

async def generate_zip_async(app_name, package_name, min_sdk, target_sdk, description, prompt):
    cfg = AndroidProjectConfig(
        app_name=(app_name or "GeneratedApp").strip(),
        package_name=(package_name or "com.example.generatedapp").strip(),
        description=description or "",
        min_sdk=int(min_sdk or 24),
        target_sdk=int(target_sdk or 34),
        prompt=(prompt or "").strip(),
    )
    data = await generate_android_project_zip(cfg)
    out_path = f"/tmp/{cfg.app_name}.zip"
    with open(out_path, "wb") as f:
        f.write(data)
    return out_path

def generate_zip(app_name, package_name, min_sdk, target_sdk, description, prompt):
    return asyncio.run(generate_zip_async(app_name, package_name, min_sdk, target_sdk, description, prompt))

with gr.Blocks(title="AI Android Generator (Space)") as demo:
    gr.Markdown("## AI Android Generator – tạo zip dự án Android (Gradle + Jetpack Compose)")
    with gr.Row():
        app_name = gr.Textbox(label="Tên ứng dụng", value="GeneratedApp")
        package_name = gr.Textbox(label="Package name", value="com.example.generatedapp")
    with gr.Row():
        min_sdk = gr.Number(label="Min SDK", value=24, precision=0)
        target_sdk = gr.Number(label="Target SDK", value=34, precision=0)
    description = gr.Textbox(label="Mô tả", value="")
    prompt = gr.Textbox(label="Prompt (yêu cầu UI/chức năng)", lines=6, placeholder="Ví dụ: ToDo app với Compose, danh sách + thêm/sửa/xóa")

    btn = gr.Button("Sinh dự án (.zip)")
    out = gr.File(label="Tải xuống zip")

    btn.click(fn=generate_zip, inputs=[app_name, package_name, min_sdk, target_sdk, description, prompt], outputs=out)

if __name__ == "__main__":
    demo.launch()