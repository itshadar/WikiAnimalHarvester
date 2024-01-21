from asyncio import Queue
from logging import getLogger
from pathlib import Path
from typing import Tuple

from aiofiles import open as aio_open
from src.handlers.async_http_client import HTTPXClient
from src.common.schemas import ImageQueueItem

logger = getLogger(__name__)


class ImageDownloader:
    """
    A class responsible for downloading images asynchronously.
    """

    def __init__(self, client: HTTPXClient, destination_dir: Path):
        """
        Initializes the ImageDownloader with an HTTP client and a destination directory.

        :param client: HTTPXClient's instance for making HTTP requests.
        :param destination_dir: Path object representing the directory where images will be saved.
        """
        self.client = client
        self.destination_dir = destination_dir

    async def download_image_consumer(self, image_queue: Queue[ImageQueueItem]):
        """
        Consumes tasks from an image queue and downloads images.

        :param image_queue: A queue containing tuples of image URL and image name.
        """
        while True:
            image_item = await image_queue.get()
            image_url, image_name = image_item.image_url, image_item.image_name
            try:
                await self.download_image(image_url, image_name)
            except (ConnectionError, OSError) as e:
                logger.error(f"Failed to download {image_name} image: {e}")
            finally:
                image_queue.task_done()

    async def download_image(self, image_url: str, image_name: str):
        """
        Downloads an image from the given URL and saves it to the destination directory.

        :param image_url: URL of the image to download.
        :param image_name: Name to save the image as.
        """
        response = await self.client.get(url=image_url)
        image_format = image_url.rsplit(".")[-1].lower()
        file_path = Path(self.destination_dir, f"{image_name}.{image_format}")
        await self.save_image(image_file_path=file_path, data=response.content)
        logger.info(f"Saved image to: {file_path}")

    async def save_image(self, image_file_path: Path, data: bytes):
        """
        Saves image data to a file.

        :param image_file_path: The file path where the image will be saved.
        :param data: Content of the image as bytes.
        """
        async with aio_open(image_file_path, mode="wb") as file:
            await file.write(data)
