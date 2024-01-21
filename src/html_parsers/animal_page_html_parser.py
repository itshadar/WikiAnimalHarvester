from bs4 import BeautifulSoup, SoupStrainer
from typing_extensions import Self

from src.html_parsers.base_html_parser import BaseHTMLParser


class AnimalWikiPageHTMLParser(BaseHTMLParser):
    """This parser reference parser to https://en.wikipedia.org/wiki/<animal_page_name>"""

    def __init__(self, soup: BeautifulSoup, resource_url: str):
        super().__init__(soup, resource_url)

    def extract_image_url(self):
        """Extract the main image url of the page resource."""
        image_meta_tag = self.soup.find("meta", property="og:image")
        try:
            image_url = image_meta_tag.get("content")
            return self.get_full_url(image_url)
        except AttributeError as e:
            raise ValueError(f"Failed to find image url at {self.resource_url}") from e

    @classmethod
    def create(cls, html_content, resource_url) -> Self:
        strainer = SoupStrainer(["meta"])
        soup = BeautifulSoup(html_content, "lxml", parse_only=strainer)
        return cls(soup=soup, resource_url=resource_url)
