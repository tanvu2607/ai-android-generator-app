from dataclasses import dataclass
from pathlib import Path
from typing import Dict
import tempfile
import shutil
import zipfile

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .llm import generate_compose_content_from_prompt

TEMPLATES_DIR = Path("backend/app/templates/android")

@dataclass
class AndroidProjectConfig:
    app_name: str
    package_name: str
    description: str
    min_sdk: int
    target_sdk: int
    prompt: str


def _create_jinja_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env


def _package_to_path(package_name: str) -> str:
    return package_name.replace(".", "/")


async def render_project(config: AndroidProjectConfig, output_dir: Path) -> None:
    env = _create_jinja_env()

    # Generate dynamic Compose content
    compose_content = await generate_compose_content_from_prompt(config.prompt)

    common_ctx: Dict[str, object] = {
        "app_name": config.app_name,
        "package_name": config.package_name,
        "package_dir": _package_to_path(config.package_name),
        "description": config.description,
        "min_sdk": config.min_sdk,
        "target_sdk": config.target_sdk,
        "compose_content": compose_content,
    }

    # Map of template path -> output relative path
    files = {
        "root/settings.gradle.kts.j2": "settings.gradle.kts",
        "root/build.gradle.kts.j2": "build.gradle.kts",
        "root/gradle.properties.j2": "gradle.properties",
        "root/.gitignore.j2": ".gitignore",
        "app/build.gradle.kts.j2": "app/build.gradle.kts",
        "app/src/main/AndroidManifest.xml.j2": "app/src/main/AndroidManifest.xml",
        "app/src/main/java/MainActivity.kt.j2": f"app/src/main/java/{common_ctx['package_dir']}/MainActivity.kt",
        "app/src/main/res/values/strings.xml.j2": "app/src/main/res/values/strings.xml",
        "app/src/main/res/values/themes.xml.j2": "app/src/main/res/values/themes.xml",
        "app/src/main/res/values/colors.xml.j2": "app/src/main/res/values/colors.xml",
        # Adaptive launcher icon assets
        "app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml.j2": "app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml",
        "app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml.j2": "app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml",
        "app/src/main/res/values/ic_launcher_background.xml.j2": "app/src/main/res/values/ic_launcher_background.xml",
        "app/src/main/res/drawable/ic_launcher_foreground.xml.j2": "app/src/main/res/drawable/ic_launcher_foreground.xml",
    }

    for template_name, out_rel in files.items():
        template = env.get_template(template_name)
        out_path = output_dir / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(template.render(**common_ctx), encoding="utf-8")


async def generate_android_project_zip(config: AndroidProjectConfig) -> bytes:
    tmp_root = Path(tempfile.mkdtemp(prefix="android_gen_"))
    project_dir = tmp_root / config.app_name
    project_dir.mkdir(parents=True, exist_ok=True)

    try:
        await render_project(config, project_dir)
        zip_path = tmp_root / f"{config.app_name}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in project_dir.rglob("*"):
                zf.write(file, arcname=str(file.relative_to(project_dir)))
        data = zip_path.read_bytes()
        return data
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)