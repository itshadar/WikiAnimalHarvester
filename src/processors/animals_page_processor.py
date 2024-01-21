import logging
from asyncio import Queue, create_task, gather
from collections import defaultdict
from typing_extensions import Self
from typing import Final

from src.handlers.image_downloader import ImageDownloader
from src.processors.animal_page_processor import AnimalPageProcessor
from src.processors.html_parsers.animals_html_parser import AnimalsHTMLParser
from src.handlers.async_http_client import HTTPXClient
from src.common.schemas import PageQueueItem, ImageQueueItem

logger = logging.getLogger(__name__)


class AnimalsPageProcessor:
    """
    A class responsible for processing animal data from Wikipedia URL:
    "https://en.wikipedia.org/wiki/List_of_animal_names".
    It processes multiple pages and images concurrently leveraging
    queues and asynchronous programming.
    """
    RESOURCE_URL: Final[str] = "https://en.wikipedia.org/wiki/List_of_animal_names"

    def __init__(self, concurrency: int, parser: AnimalsHTMLParser,
                 animal_page_processor: AnimalPageProcessor, image_downloader: ImageDownloader,
                 page_queue: Queue[PageQueueItem], image_queue: Queue[ImageQueueItem]):
        """
        Initializes the AnimalsPageProcessor with necessary components and queues.

        :param concurrency: Number of concurrent tasks to run.
        :param parser: Parser for the animals page HTML content.
        :param animal_page_processor: process single animal page content.
        :param image_downloader: Downloader for animal images.
        :param page_queue: Queue for animal page URLs.
        :param image_queue: Queue for animal image URLs.
        """
        self.concurrency = concurrency
        self.content_parser = parser
        self.animal_page_processor = animal_page_processor
        self.image_downloader = image_downloader
        self.page_queue = page_queue
        self.image_queue = image_queue
        self.collateral_adjectives_groups = defaultdict(list)

    @classmethod
    async def create(cls, client: HTTPXClient, concurrency: int, image_downloader: ImageDownloader) -> Self:
        """
        Class method to create an instance of AnimalsPageProcessor.

        :param client: HTTP client for making requests.
        :param concurrency: Number of concurrent tasks.
        :param image_downloader: Downloader for animal images.
        :return: An instance of AnimalsPageProcessor.
        """
        html_content = await cls._fetch_resource_content(client)
        parser = AnimalsHTMLParser.create(html_content=html_content, resource_url=cls.RESOURCE_URL)
        animal_page_processor = AnimalPageProcessor(client)
        return cls(concurrency, parser, animal_page_processor, image_downloader, Queue(concurrency), Queue(concurrency))

    async def run(self):
        """
        Starts the animals page processing.
        """
        await self._activate_processor_consumers()
        producers = [create_task(self._process_animals_wiki_page())]
        await gather(*producers)
        await self.page_queue.join()
        await self.image_queue.join()

    async def _process_animals_wiki_page(self):
        """
        Builds the collateral adjectives groups dictionary and puts animal page URLs into the page queue.
        """
        for animal_info in self.content_parser.parse_animal_table():
            for collateral_adjective in animal_info.collateral_adjectives:
                self.collateral_adjectives_groups[collateral_adjective].append(animal_info.name)
            page_item = PageQueueItem(page_url=animal_info.page_url, page_name=animal_info.name)
            await self.page_queue.put(page_item)

    async def _activate_processor_consumers(self):
        """
        Activates the consumers for the page and image queues.
        """
        consumers = [create_task(self.animal_page_processor.extract_animal_page_data(self.page_queue, self.image_queue))
                     for _ in range(self.concurrency)]
        consumers.extend(create_task(self.image_downloader.download_image_consumer(self.image_queue))
                         for _ in range(self.concurrency))

    @classmethod
    async def _fetch_resource_content(cls, client: HTTPXClient):
        """
        Fetches the content of the Wikipedia resource page.

        :param client: HTTP client for making requests.
        :return: The content of the Wikipedia page.
        """
        response = await client.get(url=cls.RESOURCE_URL)
        logger.info(f"Successfully fetched: {cls.RESOURCE_URL}")
        return response.content


