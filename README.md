# WikiAnimalHarvester
This program is designed to extract and output "collateral adjectives" and their corresponding "animals" from the Wikipedia page ["List of animal names"](https://en.wikipedia.org/wiki/List_of_animal_names). The program identifies each animal and its associated collateral adjectives. If an animal is associated with more than one collateral adjective, each is used and mentioned accordingly.

## Features
- **Image Downloading**: Downloads the picture of each animal into the `/tmp/` directory.
- **Asynchronous Processing**: Uses `asyncio` for non-blocking network calls and concurrent processing.
- **Queue-Based Pipeline Architecture**: Implements a pipeline architecture with `asyncio.Queue`. Tasks are queued and processed in stages, with queue size limits to manage concurrency and data processing in memory.
- **Simple Logging Mechanism**: Provides basic logging, ensuring continuous program operation even if errors occur during page fetching, crawling, or image downloading.
- **CSV Output**: Organizes and writes the collateral adjectives and corresponding animals to a CSV file.
- **Test Cases**: Includes at least two test cases.


### Prerequisites

Ensure you have Python and `pipenv` installed on your system. If not, you can install `pipenv` using pip:
``` pip install pipenv```

### Installation
Clone the repository and navigate to the project directory. Run the following command to install the required dependencies:
```pipenv install```

### Usage
```pipenv run python -m src.main```

### Testing
```pipenv run pytest .```



