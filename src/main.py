import logging
from asyncio import run
from pathlib import Path

from src.handlers.image_downloader import ImageDownloader
from src.handlers.output_writer import OutputWriter
from src.handlers.page_content_extractor import PageContentExtractor
from src.services.async_http_client import HTTPXClient
from src.wiki_animals_harvester import WikiAnimalsHarvester

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


async def main():
    current_dir = Path(__file__).parent
    tmp_directory = current_dir / "tmp"
    tmp_directory.mkdir(exist_ok=True)

    async with HTTPXClient() as client:
        page_content_extractor = PageContentExtractor(client)
        image_downloader = ImageDownloader(client, tmp_directory)
        try:
            harvester = await WikiAnimalsHarvester.create(
                client=client,
                concurrency=10,
                page_content_extractor=page_content_extractor,
                image_downloader=image_downloader,
            )
            await harvester.run()
            await OutputWriter.write_collateral_adjective_groups_to_csv(
                dir_path=current_dir,
                collateral_adjectives_groups=harvester.collateral_adjectives_groups,
            )

        except ConnectionError as e:
            logger.error(f"Connection Error: {e}")


if __name__ == "__main__":
    run(main())
