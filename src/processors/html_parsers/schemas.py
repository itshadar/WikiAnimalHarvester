from typing import Optional
from pydantic import BaseModel


class ParsedAnimalData(BaseModel):
    name: str
    collateral_adjectives: list[str]
    page_url: Optional[str]
