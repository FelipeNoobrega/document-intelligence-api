from fastapi import Depends, Header, HTTPException, status

from api.settings import Settings, get_settings

def verify_api_key(
        x_api_key: str | None = Header(default=None),
        settings: Settings = Depends(get_settings),
) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Missing API key.",
        )