from argparse import ArgumentParser, Namespace
from pathlib import Path

CLIargs = Namespace


def get_args() -> CLIargs:
    """Get user input from the command-line and parse it."""
    parser = ArgumentParser(description="Download files uploaded with git-annex.")
    parser.add_argument(
        "files",
        help="Files to download.",
        nargs='+',
        type=Path,
    )
    parser.add_argument(
        "-c",
        "--cloud_provider",
        choices=["azure", "s3"],
        default="s3",
        help="Cloud storage provider to use.",
        type=str,
    )
    parser.add_argument(
        "--not_symlinks",
        action="store_true",
        default=False,
        help="Use paths that are not symlinks?",
    )
    args = parser.parse_args()
    return args
