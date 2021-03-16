import itertools
import os
from pathlib import Path
from typing import Iterable

from . import amazon_s3, azure_storage_blob, cli_args, loggers, utils
from .exceptions import DownloadException

CONTAINER_NAME = "git-annex"
logger = loggers.get_logger()


def get_connection_string() -> str:
    try:
        conn_string = os.environ["STORAGE_CONNECTION_STRING"]
    except KeyError:
        msg = "Could not find 'STORAGE_CONNECTION_STRING' env var."
        raise EnvironmentError(msg)
    return conn_string


def download_file(file_path: Path):
    symlink_path = Path(file_path)
    if not symlink_path.is_symlink():
        raise ValueError(f"'{symlink_path}' is not a symlink.")

    file_key = utils.lookup_key(symlink_path)  # SHA256E-s1024--81a9ef8...
    file_size = utils.get_file_size_from_key(file_key)
    if not utils.needs_download(file_path, file_size):
        logger.info(f"Skipping already downloaded \n\t '{file_path}'.")
    else:
        conn_string = get_connection_string()
        azure = azure_storage_blob.AzureAPI(conn_string)
        resolved_path = symlink_path.resolve()
        utils.mkdirs(resolved_path)
        logger.info(f"Downloading '{file_path}'...")
        azure.download(CONTAINER_NAME, file_key, resolved_path)
    logger.info(f"ok")


def download(files: Iterable[Path]):
    for result, file in utils.map_parallel(download_file, files):
        if not result:
            raise DownloadException(result, file)


def expand_and_filter_paths(
    paths: Iterable[Path], allow_not_symlinks: bool = False
) -> Iterable[Path]:
    files = itertools.chain(
        *[path.rglob(r"*") if path.is_dir() else [path] for path in paths]
    )
    if allow_not_symlinks:
        files = filter(Path.is_file, files)
    else:
        files = filter(Path.is_symlink, files)
    return files


def main():
    args = cli_args.get_args()
    files = expand_and_filter_paths(args.files, args.not_symlinks)
    if args.cloud_provider == "s3":
        for file_path in files:
            amazon_s3.lookup_download_decrypt(file_path)
    else:
        download(files)
