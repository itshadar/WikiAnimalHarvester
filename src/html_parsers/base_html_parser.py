from abc import ABC, abstractmethod
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from typing_extensions import Self


class BaseHTMLParser(ABC):
    """This base parser uses Beautiful Soup as the base HTML parser."""

    def __init__(self, soup: BeautifulSoup, resource_url: str):
        """
        Initialize the parser with a BeautifulSoup object and the URL of the HTML page.

        :param soup: BeautifulSoup object to parse HTML.
        :param resource_url: The URL of the HTML page resource.
        """
        self.soup = soup
        self.resource_url = resource_url

    def get_full_url(self, link: str) -> str:
        """Return the full URL that the link refer to based on the resource page URL."""
        return urljoin(self.resource_url, link)

    @classmethod
    @abstractmethod
    def create(cls, html_content: str, resource_url: str) -> Self:
        """
        Create an instance of the subclass with the given HTML content and resource URL.
        This is an abstract method that must be implemented by subclasses.

        :param html_content: The raw HTML content to parse.
        :param resource_url: The URL of the HTML page resource.
        :return: An instance of the subclass.
        """
        pass
