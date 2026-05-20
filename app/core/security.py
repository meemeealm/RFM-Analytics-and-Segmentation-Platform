from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import Settings, get_settings


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key_placeholder(
    api_key: str | None = Depends(api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    configured_api_key = settings.api_key

    if not configured_api_key:
        return

    if api_key != configured_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
