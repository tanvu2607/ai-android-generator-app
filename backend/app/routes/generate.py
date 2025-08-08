from fastapi import APIRouter, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from io import BytesIO

from ..services.generator import AndroidProjectConfig, generate_android_project_zip

router = APIRouter()

class GenerateRequest(BaseModel):
    app_name: str = Field(...)
    package_name: str = Field(...)
    description: Optional[str] = Field(default=None)
    min_sdk: int = Field(default=24)
    target_sdk: int = Field(default=34)
    prompt: str = Field(...)

@router.post("/generate")
async def generate(
    app_name: str = Form(...),
    package_name: str = Form(...),
    prompt: str = Form(...),
    description: Optional[str] = Form(None),
    min_sdk: int = Form(24),
    target_sdk: int = Form(34),
):
    config = AndroidProjectConfig(
        app_name=app_name,
        package_name=package_name,
        description=description or "",
        min_sdk=min_sdk,
        target_sdk=target_sdk,
        prompt=prompt,
    )

    zip_bytes = await generate_android_project_zip(config)
    buffer = BytesIO(zip_bytes)
    headers = {"Content-Disposition": "attachment; filename=android-project.zip"}
    return StreamingResponse(buffer, media_type="application/zip", headers=headers)