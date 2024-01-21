from typing import Final, Optional

from pydantic import BaseModel


# Constants section #
class AnimalTableHeaders:
    ANIMAL: Final[str] = "Animal"
    COLLATERAL_ADJECTIVE: Final[str] = "Collateral adjective"


class AnimalTableHTMLSetting:
    SPAN_ID: Final[str] = "Terms_by_species_or_taxon"
    TABLE_CLASS: Final[str] = "wikitable sortable"


# Schemas section #
class ParsedAnimalData(BaseModel):
    name: str
    collateral_adjectives: list[str]
    page_url: Optional[str]
