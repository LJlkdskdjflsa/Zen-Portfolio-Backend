from pydantic import BaseModel
from typing import Any

class TokenBalanceResponse(BaseModel):
    block_number: int
    cursor: str | None
    page: int
    page_size: int
    result: list[dict[str, Any]]
