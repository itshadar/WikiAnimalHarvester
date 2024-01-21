import logging
from pathlib import Path

import aiofiles

logger = logging.getLogger(__name__)


class OutputWriter:
    @staticmethod
    async def write_collateral_adjective_groups_to_csv(
        dir_path: Path, collateral_adjectives_groups: dict[str, list[str]]
    ):
        file_path = dir_path / "collateral_adjectives_animals_groups.csv"
        try:
            async with aiofiles.open(file_path, mode="w") as file:
                await file.write("Collateral Adjective,Animals\n")
                for (
                    collateral_adjective,
                    animals,
                ) in collateral_adjectives_groups.items():
                    animals_list = ",".join(animals)
                    await file.write(
                        f'"{collateral_adjective.capitalize()}","{animals_list}"\n'
                    )

            logger.info(f"CSV file saved: {file_path}")

        except PermissionError as e:
            logger.error(f"Permission error while saving file {file_path}: {e}")

    # Future method implementations for other formats like HTML
