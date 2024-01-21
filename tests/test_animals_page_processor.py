from asyncio import Queue
from unittest.mock import MagicMock

import pytest

from src.handlers.image_downloader import ImageDownloader
from src.processors.animal_page_processor import AnimalPageProcessor
from src.processors.html_parsers.animals_html_parser import AnimalsHTMLParser
from src.processors.html_parsers.schemas import ParsedAnimalData
from src.processors.animals_page_processor import AnimalsPageProcessor
from src.common.schemas import PageQueueItem

@pytest.fixture
def mock_parsed_animals():
    return [
        ParsedAnimalData(
            name="Animal1",
            collateral_adjectives=["Test1"],
            page_url="https://test/wiki/Animal1",
        ),
        ParsedAnimalData(
            name="Animal2",
            collateral_adjectives=["Test2"],
            page_url="https://test/wiki/Animal2",
        ),
        ParsedAnimalData(
            name="Animal3",
            collateral_adjectives=["Test2"],
            page_url="https://test/wiki/Animal3",
        ),
    ]


@pytest.fixture
def mock_animals_processor(mock_parsed_animals):
    """This mock processor is mocked for tests that use the process_wiki_page method"""
    # Initialize the mock objects
    mock_content_parser = MagicMock(spec=AnimalsHTMLParser)
    mock_content_parser.parse_animal_table.return_value = iter(mock_parsed_animals)
    animal_page_processor_mock = MagicMock(spec=AnimalPageProcessor)
    image_downloader_mock = MagicMock(spec=ImageDownloader)
    page_queue = Queue()
    image_queue = Queue()

    # Create the processor with the mock objects
    mock_processor = AnimalsPageProcessor(
        concurrency=3,
        parser=mock_content_parser,
        animal_page_processor=animal_page_processor_mock,
        image_downloader=image_downloader_mock,
        page_queue=page_queue,
        image_queue=image_queue,
    )

    return mock_processor


class TestAnimalsPageProcessor:
    @pytest.mark.asyncio
    async def test_process_wiki_page_queue_size(
        self, mock_animals_processor, mock_parsed_animals
    ):
        # run method
        await mock_animals_processor._process_animals_wiki_page()

        # assert that the queue populate as expected
        assert mock_animals_processor.page_queue.qsize() == len(
            mock_parsed_animals
        )

        for animal_info in mock_parsed_animals:
            queued_item = await mock_animals_processor.page_queue.get()
            excepted_item = PageQueueItem(page_url=animal_info.page_url, page_name=animal_info.name)
            assert queued_item == excepted_item

    @pytest.mark.asyncio
    async def test_process_wiki_page(
        self, mock_animals_processor, mock_parsed_animals
    ):
        # run method
        await mock_animals_processor._process_animals_wiki_page()
        excepted_collateral_adjectives_groups = {
            "Test2": ["Animal2", "Animal3"],
            "Test1": ["Animal1"],
        }
        assert (
            excepted_collateral_adjectives_groups
            == mock_animals_processor.collateral_adjectives_groups
        )
