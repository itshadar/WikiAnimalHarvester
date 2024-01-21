import logging
from pathlib import Path

import aiofiles

logger = logging.getLogger(__name__)


class OutputWriter:
    """
    A class responsible for writing output data to various file formats.
    Currently supports writing data to CSV files.
    """

    @staticmethod
    async def write_adjectives_groups_to_csv(dir_path: Path, collateral_adjectives_groups: dict[str, list[str]]):
        """
        Writes collateral adjectives animal groups to a CSV file.

        :param dir_path: The directory path where the CSV file will be saved.
        :param collateral_adjectives_groups: Dictionary where keys are collateral adjectives
                                             and values are lists of animals (associated with these adjectives).
        """
        file_path = dir_path / "collateral_adjectives_animals_groups.csv"
        try:
            async with aiofiles.open(file_path, mode="w") as file:
                await file.write("Collateral Adjective,Animals\n")
                for collateral_adjective, animals in collateral_adjectives_groups.items():
                    animals_list = ",".join(animals)
                    await file.write(f'"{collateral_adjective.capitalize()}","{animals_list}"\n')
            logger.info(f"CSV file saved: {file_path}")

        except PermissionError as e:
            logger.error(f"Permission error while saving file {file_path}: {e}")

    # Future method implementations for other formats like HTML
