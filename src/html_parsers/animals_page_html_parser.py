import logging
from pydantic import ValidationError
from bs4 import SoupStrainer, BeautifulSoup, Tag
from typing_extensions import Self
from typing import Optional, Iterator
from src.html_parsers.utils import AnimalTableHeaders, AnimalTableHTMLSetting, ParsedAnimalData
from src.html_parsers.base_html_parser import BaseHTMLParser


logger = logging.getLogger(__name__)


class AnimalsPageWikiHTMLParser(BaseHTMLParser):
    """
    This parser reference parser to "https://en.wikipedia.org/wiki/List_of_animal_names"
    """

    def __init__(self, soup: BeautifulSoup, resource_url: str):
        super().__init__(soup, resource_url)

    @classmethod
    def create(cls, html_content, resource_url) -> Self:
        strainer = SoupStrainer(["span", "table"])
        soup = BeautifulSoup(html_content, 'lxml', parse_only=strainer)
        return cls(soup=soup, resource_url=resource_url)

    def parse_animal_table(self) -> Iterator[ParsedAnimalData]:
        """Parse the html animal table."""
        table = self._get_table(span_id=AnimalTableHTMLSetting.SPAN_ID,
                                table_class=AnimalTableHTMLSetting.TABLE_CLASS)
        if table:
            table_headers = self._get_table_headers(table)
            self._validate_animal_table_headers(table_headers)

            for parsed_row in self._parse_animal_table_rows(table, table_headers):
                yield parsed_row

        else:
            raise ValueError(f"Failed to find the animals table at {self.resource_url}.")

    @classmethod
    def _validate_animal_table_headers(cls, table_headers: dict[str, int]) -> None:
        """Validates animal table headers."""
        missing_headers = {AnimalTableHeaders.ANIMAL, AnimalTableHeaders.COLLATERAL_ADJECTIVE}.difference(table_headers)

        if len(missing_headers) > 0:
            raise ValueError(f"The following table headers are missing: {','.join(missing_headers)}\n")

    def _get_table(self, span_id: str, table_class: str) -> Optional[Tag]:
        """Find and return table that appear after specific span tag and by table class value."""
        span_tag = self.soup.find('span', id=span_id)
        return span_tag.find_next('table', {'class': table_class}) if span_tag else None

    def _get_table_headers(self, table: Tag) -> dict[str, int]:
        """Map table headers to their indices."""
        headers = [header.get_text(strip=True) for header in table.find_next('tr').find_all('th')]
        return dict(zip(headers, range(len(headers))))

    def _extract_animal_collateral_adjectives(self, cells: list[Tag], table_headers: dict) -> Optional[list[str]]:
        """Extract collateral adjectives values, without references."""
        collateral_adjectives_cell = cells[table_headers[AnimalTableHeaders.COLLATERAL_ADJECTIVE]]

        # Remove references
        for sup in collateral_adjectives_cell.find_all('sup'):
            sup.decompose()

        # Extract adjectives
        collateral_adjectives = collateral_adjectives_cell.get_text(separator=',').split(",")

        if collateral_adjectives[0] not in ['—', '']:
            # collateral adjectives' cell is not empty
            return collateral_adjectives

    def _extract_animal_info(self, cells: list[Tag], table_headers: dict[str, int]) -> tuple[Optional[str], Optional[str]]:
        animal_cell = cells[table_headers[AnimalTableHeaders.ANIMAL]]
        try:
            animal_a_tag = animal_cell.find('a')
            animal_page_url, animal_name = self.get_full_url(animal_a_tag.get('href')), animal_a_tag.get('title')
            return animal_page_url, animal_name

        except AttributeError as e:
            logger.error(f"Failed to extract animal name and URL from the content: {animal_cell}")

    def _parse_animal_row(self, row: Tag, table_headers: dict[str, int]) -> Optional[ParsedAnimalData]:
        """Parse row cells based on table's headers mapping."""
        cells = row.find_all('td')

        if len(cells) == len(table_headers):
            animal_page_url, animal_name = self._extract_animal_info(cells, table_headers)
            adjectives = self._extract_animal_collateral_adjectives(cells, table_headers)
            try:
                return ParsedAnimalData(page_url=animal_page_url, name=animal_name, collateral_adjectives=adjectives)

            except ValidationError as e:
                logger.error(f"Row of animal {animal_name} has missing arguments")

    def _parse_animal_table_rows(self, table: Tag, table_headers: dict) -> Iterator[ParsedAnimalData]:
        """Iterate and parse all table rows."""
        for row in table.find_all('tr')[1:]:
            parsed_row: Optional[ParsedAnimalData] = self._parse_animal_row(row, table_headers)
            if parsed_row:
                yield parsed_row
