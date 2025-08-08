import asyncio
from pathlib import Path
import typer

from backend.app.services.generator import AndroidProjectConfig, generate_android_project_zip

app = typer.Typer(add_completion=False, help="AI Android Generator CLI")


@app.command("gen")
def generate(
    app_name: str = typer.Option(..., "-n", "--app-name", help="Tên ứng dụng / Project name"),
    package_name: str = typer.Option(..., "-p", "--package-name", help="Android package name, ví dụ com.example.app"),
    prompt: str = typer.Option(..., "-r", "--prompt", help="Yêu cầu UI/Chức năng"),
    description: str = typer.Option("", "-d", "--description", help="Mô tả"),
    min_sdk: int = typer.Option(24, "--min-sdk", help="Min SDK"),
    target_sdk: int = typer.Option(34, "--target-sdk", help="Target SDK"),
    out: Path = typer.Option(Path("android-project.zip"), "-o", "--out", help="Đường dẫn file zip output"),
):
    config = AndroidProjectConfig(
        app_name=app_name,
        package_name=package_name,
        description=description,
        min_sdk=min_sdk,
        target_sdk=target_sdk,
        prompt=prompt,
    )

    zip_bytes = asyncio.run(generate_android_project_zip(config))
    out.write_bytes(zip_bytes)
    typer.echo(f"Wrote {out.resolve()} ({len(zip_bytes)} bytes)")


if __name__ == "__main__":
    app()