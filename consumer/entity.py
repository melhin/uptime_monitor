from http import HTTPStatus
from typing import Optional
from pydantic import BaseModel


class SiteResponse(BaseModel):
    up_status: str
    url: str
    id: int

    response_code: Optional[HTTPStatus] = None
    response_headers: Optional[str] = None
    response_text: Optional[str] = None
    response_time: Optional[float] = None
