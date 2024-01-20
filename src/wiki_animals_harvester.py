import logging
from collections import defaultdict
from asyncio import gather, Queue, create_task
from typing import Final
from src.handlers.image_downloader import ImageDownloader
from src.handlers.page_content_extractor import PageContentExtractor
from src.html_parsers.animals_page_html_parser import AnimalsPageWikiHTMLParser
from src.services.async_http_client import HTTPXClient

logger = logging.getLogger(__name__)


class WikiAnimalsHarvester:

    RESOURCE_URL: Final[str] = "https://en.wikipedia.org/wiki/List_of_animal_names"

    def __init__(self, concurrency: int, content_parser: AnimalsPageWikiHTMLParser,
                 page_content_extractor: PageContentExtractor, image_downloader: ImageDownloader, page_queue: Queue,
                 image_queue: Queue):

        self.concurrency = concurrency
        self.content_parser = content_parser
        self.page_content_extractor = page_content_extractor
        self.image_downloader = image_downloader
        self.page_queue = page_queue
        self.image_queue = image_queue
        self.collateral_adjectives_groups: dict[str, list[str]] = defaultdict(list)

    @classmethod
    async def create(cls, client: HTTPXClient, concurrency: int,
                     page_content_extractor: PageContentExtractor,
                     image_downloader: ImageDownloader):

        html_content = await cls.fetch_resource_content(client)
        content_parser = cls.get_content_parser(html_content)
        return cls(concurrency=concurrency,
                   content_parser=content_parser,
                   page_content_extractor=page_content_extractor,
                   image_downloader=image_downloader,
                   page_queue=Queue(concurrency),
                   image_queue=Queue(concurrency))

    @classmethod
    def get_content_parser(cls, html_content: str):
        return AnimalsPageWikiHTMLParser.create(html_content=html_content, resource_url=cls.RESOURCE_URL)

    @classmethod
    async def fetch_resource_content(cls, client: HTTPXClient):
        """Fetch resource content."""
        response = await client.get(url=cls.RESOURCE_URL)
        logger.info(f"Successfully fetch: {cls.RESOURCE_URL}")
        return response.content

    async def process_animals_wiki_page(self):
        """Build the collateral adjectives groups dictionary and put animal page in the pages queue."""
        for animal_info in self.content_parser.parse_animal_table():
            for collateral_adjective in animal_info.collateral_adjectives:
                self.collateral_adjectives_groups[collateral_adjective].append(animal_info.name)
            await self.page_queue.put((animal_info.page_url, animal_info.name))

    async def _activate_harvester_consumers(self):
        consumers = [create_task(
            self.page_content_extractor.extract_animal_html_page_image_url_consumer(self.page_queue, self.image_queue))
            for _ in range(self.concurrency)]
        consumers.extend(create_task(self.image_downloader.download_image_consumer(self.image_queue))
                         for _ in range(self.concurrency))

    async def run(self):
        await self._activate_harvester_consumers()
        producers = [create_task(self.process_animals_wiki_page())]
        await gather(*producers)
        await self.page_queue.join()
        await self.image_queue.join()
