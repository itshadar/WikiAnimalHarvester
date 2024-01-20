import pytest
from src.html_parsers.animals_page_html_parser import AnimalsPageWikiHTMLParser
from src.html_parsers.utils import ParsedAnimalData


@pytest.fixture()
def mock_html_content():
    return """
    <html>
    <h2><span class="mw-headline" id="Terms_by_species_or_taxon">Terms by species or taxon</span></h2>
    <table class="wikitable sortable" style="text-align:left;">
    <tbody>
    <tr>
    <th>Animal</th>    
    <th>Collateral adjective</th>
    </tr>
    <tr>
    <td><a href="/wiki/Animal1" title="Animal1">Animal1</a></td>
    <td>Test1</td>
    </tr>
    <tr>
    <td><a href="/wiki/Animal2" title="Animal2">Animal2</a></td>
    <td>Test2</td>
    </tr>
    <tr>
    <td><a href="/wiki/Animal3" title="Animal3">Animal3</a></td>
    <td>Test2</td>
    </tr>
    </tbody></table>
    </html>
    """


@pytest.fixture()
def mock_animals_page_html_parser(mock_html_content):
    return AnimalsPageWikiHTMLParser.create(html_content=mock_html_content, resource_url="https://test")


class TestAnimalsPageHTMLParser:

    def test_parse_animal_table(self, mock_animals_page_html_parser):

        parsed_animals = [parsed_animal for parsed_animal in mock_animals_page_html_parser.parse_animal_table()]
        excepted_parsed_animals = [ParsedAnimalData(name="Animal1",
                                                    collateral_adjectives=["Test1"],
                                                    page_url="https://test/wiki/Animal1"),
                                   ParsedAnimalData(name="Animal2",
                                                    collateral_adjectives=["Test2"],
                                                    page_url="https://test/wiki/Animal2"),
                                   ParsedAnimalData(name="Animal3",
                                                    collateral_adjectives=["Test2"],
                                                    page_url="https://test/wiki/Animal3")
                                   ]

        assert excepted_parsed_animals == parsed_animals
