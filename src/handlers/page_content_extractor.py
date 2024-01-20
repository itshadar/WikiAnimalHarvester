from asyncio import Queue
from logging import getLogger
from src.services.async_http_client import HTTPXClient
from src.html_parsers.animal_page_html_parser import AnimalWikiPageHTMLParser

logger = getLogger(__name__)


class PageContentExtractor:

    def __init__(self, client: HTTPXClient):
        self.client = client

    async def extract_animal_html_page_image_url_consumer(self, page_queue: Queue, image_queue: Queue):

        while True:
            page_url, page_name = await page_queue.get()
            try:
                response = await self.client.get(url=page_url)
                image_url = AnimalWikiPageHTMLParser.create(html_content=response.text, resource_url=page_url).extract_image_url()
                logger.info(f"Successfully process {page_url}")
                await image_queue.put((image_url, page_name))

            except ValueError as e:
                logger.error(f"Error processing {page_name} page: {e}")

            except ConnectionError as e:
                logger.error(f"Error fetching {page_name} page: {e}")

            finally:
                page_queue.task_done()
