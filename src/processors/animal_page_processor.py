from asyncio import Queue
from logging import getLogger

from src.processors.html_parsers.animal_html_parser import AnimalHTMLParser
from src.handlers.async_http_client import HTTPXClient
from src.common.schemas import PageQueueItem, ImageQueueItem

logger = getLogger(__name__)


class AnimalPageProcessor:
    """
    A class responsible for extracting data from animal wiki pages given animal's page URL.
    """

    def __init__(self, client: HTTPXClient):
        self.client = client

    async def extract_animal_page_data(self, page_queue: Queue[PageQueueItem], image_queue: Queue[ImageQueueItem]):
        """
        Asynchronously consumes page URLs from a queue, extracts relevant data from each page,
        and puts the extracted data into the image queue.

        :param page_queue: containing items (PageQueueItem) with the names and URLs of animal pages.
        :param image_queue: containing items (ImageQueueItem) with the extracted image URL and page name.
        """
        while True:
            page_item = await page_queue.get()
            page_name, page_url = page_item.page_name, page_item.page_url
            try:
                response = await self.client.get(url=page_url)
                parser = AnimalHTMLParser.create(
                    html_content=response.text, resource_url=page_url
                )
                image_url = parser.extract_image_url()
                logger.info(f"Successfully processed {page_url}")
                image_item = ImageQueueItem(image_url=image_url, image_name=page_name)
                await image_queue.put(image_item)

            except ValueError as e:
                logger.error(f"Error processing {page_name} page: {e}")

            except ConnectionError as e:
                logger.error(f"Error fetching {page_name} page: {e}")

            finally:
                page_queue.task_done()
