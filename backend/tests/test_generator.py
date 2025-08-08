import asyncio
from pathlib import Path
from backend.app.services.generator import AndroidProjectConfig, render_project
import tempfile

async def _gen(tmp: Path):
    config = AndroidProjectConfig(
        app_name="DemoApp",
        package_name="com.example.demo",
        description="desc",
        min_sdk=24,
        target_sdk=34,
        prompt="Simple screen with a title and a button",
    )
    await render_project(config, tmp / config.app_name)


def test_render_project_writes_files(tmp_path: Path):
    asyncio.run(_gen(tmp_path))
    base = tmp_path / "DemoApp"
    assert (base / "settings.gradle.kts").exists()
    assert (base / "build.gradle.kts").exists()
    assert (base / "app" / "build.gradle.kts").exists()
    assert (base / "app" / "src" / "main" / "AndroidManifest.xml").exists()
    assert (base / "app" / "src" / "main" / "res" / "values" / "strings.xml").exists()