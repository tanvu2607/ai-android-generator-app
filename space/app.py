import asyncio
import os
import gradio as gr

from backend.app.services.generator import AndroidProjectConfig, generate_android_project_zip

# ---------- Core generate helpers ----------
async def _generate_zip_async(app_name, package_name, min_sdk, target_sdk, description, prompt):
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
    return asyncio.run(_generate_zip_async(app_name, package_name, min_sdk, target_sdk, description, prompt))

# ---------- Prompt builder ----------
def build_prompt(base_desc, presets, arch, data, ui, theme):
    lines = []
    if presets:
        lines.append(f"Loại app: {', '.join(presets)}")
    if arch:
        lines.append(f"Kiến trúc: {', '.join(arch)}")
    if data:
        lines.append(f"Data layer: {', '.join(data)}")
    if ui:
        lines.append(f"Thành phần UI: {', '.join(ui)}")
    if theme:
        lines.append(f"Theme: {', '.join(theme)}")
    base_desc = (base_desc or "").strip()
    if base_desc:
        lines.append(f"Mô tả bổ sung: {base_desc}")
    return "\n".join(lines)

# Compose the UI
with gr.Blocks(title="AI Android Generator (Space)") as demo:
    gr.Markdown("""
    # AI Android Generator
    Tạo file .zip dự án Android (Gradle + Jetpack Compose) từ yêu cầu của bạn. Chỉ là giao diện tạo zip; build APK/AAB nên thực hiện bằng GitHub Actions trong repo.
    """)

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Cấu hình dự án")
            app_name = gr.Textbox(label="Tên ứng dụng", value="GeneratedApp")
            package_name = gr.Textbox(label="Package name", value="com.example.generatedapp")
            with gr.Row():
                min_sdk = gr.Number(label="Min SDK", value=24, precision=0)
                target_sdk = gr.Number(label="Target SDK", value=34, precision=0)
            description = gr.Textbox(label="Mô tả", value="")

            gr.Markdown("### Prompt")
            base_desc = gr.Textbox(label="Mô tả yêu cầu (tự do)", lines=6, placeholder="Ví dụ: ToDo app với Compose, danh sách + thêm/sửa/xóa")

            generate_btn = gr.Button("Sinh dự án (.zip)", variant="primary")
            zip_out = gr.File(label="Tải xuống zip")
        
        with gr.Column():
            gr.Markdown("### Preset & Tùy chọn (hệ thống sẽ tự tổng hợp vào prompt)")
            presets = gr.CheckboxGroup(["ToDo", "News", "Chat", "Shop"], label="Loại app", value=["ToDo"]) 
            arch = gr.CheckboxGroup(["MVVM", "Hilt DI", "Navigation Compose"], label="Kiến trúc", value=["MVVM", "Hilt DI", "Navigation Compose"]) 
            data = gr.CheckboxGroup(["Room", "Datastore", "Retrofit API + caching"], label="Data layer")
            ui = gr.CheckboxGroup(["danh sách", "mạng lưới", "thanh tìm kiếm", "form CRUD", "bottom navigation", "tabs", "settings"], label="Thành phần UI")
            theme = gr.CheckboxGroup(["Material3", "Dark mode"], label="Theme", value=["Material3", "Dark mode"]) 

            gr.Markdown("### Live Prompt Preview")
            prompt_preview = gr.Code(label="Prompt", language="markdown", interactive=False)
            build_btn = gr.Button("Gợi ý prompt từ tùy chọn")

    # Events
    def _update_preview(base_desc, presets, arch, data, ui, theme):
        return build_prompt(base_desc, presets, arch, data, ui, theme)

    for src in (base_desc, presets, arch, data, ui, theme):
        src.change(_update_preview, inputs=[base_desc, presets, arch, data, ui, theme], outputs=prompt_preview)
    build_btn.click(_update_preview, inputs=[base_desc, presets, arch, data, ui, theme], outputs=prompt_preview)

    def _on_generate(app_name, package_name, min_sdk, target_sdk, description, base_desc, presets, arch, data, ui, theme, preview_text):
        prompt_text = (base_desc or "").strip()
        if not prompt_text:
            prompt_text = build_prompt(base_desc, presets, arch, data, ui, theme)
        if not prompt_text:
            prompt_text = "Màn hình danh sách đơn giản với Material3"
        return generate_zip(app_name, package_name, min_sdk, target_sdk, description, prompt_text)

    generate_btn.click(_on_generate,
        inputs=[app_name, package_name, min_sdk, target_sdk, description, base_desc, presets, arch, data, ui, theme, prompt_preview],
        outputs=zip_out)

if __name__ == "__main__":
    demo.launch()