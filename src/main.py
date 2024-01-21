import logging
from asyncio import run
from pathlib import Path

from src.handlers.image_downloader import ImageDownloader
from src.handlers.output_writer import OutputWriter
from src.handlers.async_http_client import HTTPXClient
from src.processors.animals_page_processor import AnimalsPageProcessor

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


async def main():
    """The main function of the application."""

    # Set up output destination directories.
    current_dir = Path(__file__).parent
    tmp_directory = current_dir / "tmp"
    tmp_directory.mkdir(exist_ok=True)

    async with HTTPXClient() as client:

        image_downloader = ImageDownloader(client, tmp_directory)
        try:
            animals_processor = await AnimalsPageProcessor.create(
                client=client,
                concurrency=10,
                image_downloader=image_downloader,
            )
            await animals_processor.run()
            await OutputWriter.write_adjectives_groups_to_csv(
                dir_path=current_dir,
                collateral_adjectives_groups=animals_processor.collateral_adjectives_groups,
            )

        except ConnectionError as e:
            logger.error(f"Connection Error: {e}")


if __name__ == "__main__":
    run(main())
