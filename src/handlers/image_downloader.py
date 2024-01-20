from asyncio import Queue
from pathlib import Path
from src.services.async_http_client import HTTPXClient
from aiofiles import open as aio_open
from logging import getLogger
from typing import Tuple

logger = getLogger(__name__)


class ImageDownloader:
    def __init__(self, client: HTTPXClient, dst_dir: Path):
        self.client = client
        self.dst_dir = dst_dir

    async def download_image_consumer(self, image_queue: Queue[Tuple[str, str]]):
        while True:
            image_url, image_name = await image_queue.get()
            try:
                await self.download_image(image_url, image_name)
            except (ConnectionError, OSError) as e:
                logger.error(f"Failed to download {image_name} image: {e}")
            finally:
                image_queue.task_done()

    async def download_image(self, image_url: str, image_name: str):
        response = await self.client.get(url=image_url)
        image_format = image_url.rsplit(".")[-1].lower()
        file_path = Path(self.dst_dir, f"{image_name}.{image_format}")
        await self.save_image(image_file_path=file_path, data=response.content)
        logger.info(f"Saved image to: {file_path}")

    async def save_image(self, image_file_path: Path, data: bytes):
        async with aio_open(image_file_path, mode='wb') as file:
            await file.write(data)
