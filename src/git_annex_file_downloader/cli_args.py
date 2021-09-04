from pathlib import Path
from typing import List, Literal

from tap import Tap as TypedArgumentParser


class GadownArgParser(TypedArgumentParser):
    files: List[Path]  # Files to download.
    store: Literal["azure-blob", "aws-s3"] = "aws-s3"  # Cloud storage provider.
    no_annex: bool = False  # Use alternative data sources for annex metadata?
    workers: int = 1  # Number of parallel downloads.

    def configure(self) -> None:
        super().configure()
        self.description = "Download files uploaded with git-annex."


def get_args() -> GadownArgParser:
    """Get user input from the command-line and parse it."""
    parser = GadownArgParser(underscores_to_dashes=True)
    args = parser.parse_args()
    return args
