import pytest
from unittest.mock import MagicMock
from asyncio import Queue
from src.html_parsers.animals_page_html_parser import AnimalsPageWikiHTMLParser
from src.html_parsers.utils import ParsedAnimalData
from src.wiki_animals_harvester import WikiAnimalsHarvester
from src.handlers.page_content_extractor import PageContentExtractor
from src.handlers.image_downloader import ImageDownloader


@pytest.fixture
def mock_parsed_animals():
    return [ParsedAnimalData(name="Animal1",
                             collateral_adjectives=["Test1"],
                             page_url="https://test/wiki/Animal1"),
            ParsedAnimalData(name="Animal2",
                             collateral_adjectives=["Test2"],
                             page_url="https://test/wiki/Animal2"),
            ParsedAnimalData(name="Animal3",
                             collateral_adjectives=["Test2"],
                             page_url="https://test/wiki/Animal3")
            ]


@pytest.fixture
def mock_wiki_animals_harvester(mock_parsed_animals):
    """This mock harvester is mocked for tests that use the process_wiki_page method"""
    # Initialize the mock objects
    mock_content_parser = MagicMock(spec=AnimalsPageWikiHTMLParser)
    mock_content_parser.parse_animal_table.return_value = iter(mock_parsed_animals)
    page_content_extractor_mock = MagicMock(spec=PageContentExtractor)
    image_downloader_mock = MagicMock(spec=ImageDownloader)
    page_queue = Queue()
    image_queue = Queue()

    # Create the processor with the mock objects
    mock_harvester = WikiAnimalsHarvester(
        concurrency=3,
        content_parser=mock_content_parser,
        page_content_extractor=page_content_extractor_mock,
        image_downloader=image_downloader_mock,
        page_queue=page_queue,
        image_queue=image_queue)

    return mock_harvester


class TestWikiAnimalsHarvester:

    @pytest.mark.asyncio
    async def test_process_wiki_page_queue_size(self, mock_wiki_animals_harvester, mock_parsed_animals):

        # run method
        await mock_wiki_animals_harvester.process_animals_wiki_page()

        # assert that the queue populate as expected
        assert mock_wiki_animals_harvester.page_queue.qsize() == len(mock_parsed_animals)

        for animal_info in mock_parsed_animals:
            queued_item = await mock_wiki_animals_harvester.page_queue.get()
            assert queued_item == (animal_info.page_url, animal_info.name)

    @pytest.mark.asyncio
    async def test_process_wiki_page(self, mock_wiki_animals_harvester, mock_parsed_animals):
        # run method
        await mock_wiki_animals_harvester.process_animals_wiki_page()
        excepted_collateral_adjectives_groups = {"Test2": ["Animal2", "Animal3"], "Test1": ["Animal1"]}
        assert excepted_collateral_adjectives_groups == mock_wiki_animals_harvester.collateral_adjectives_groups
