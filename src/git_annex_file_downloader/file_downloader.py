from __future__ import annotations

import itertools
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator

from . import amazon_s3, azure_storage_blob, cli_args, loggers, utils
from .exceptions import DownloadException


logger = loggers.get_logger()


def download(
    files: Iterable[Path],
    downloader_func: Callable[[Path], None],
    extra_args: Iterable[Any],
    workers: int,
):
    if workers > 1:
        for result, file in utils.map_parallel(
            downloader_func, files, extra_args, workers
        ):
            if not result:
                raise DownloadException(result, file)
    else:
        for f in files:
            downloader_func(f, *extra_args)


def expand_paths(paths: Iterable[Path]) -> Iterator[Path]:
    # TODO expand from large_files.json as well
    files = itertools.chain(
        *[path.rglob(r"*") if path.is_dir() else [path] for path in paths]
    )
    return files


def main():
    args = cli_args.get_args()
    if args.no_annex:
        logger.info("Downloading files without git-annex")
    logger.debug(f"From {args.store}.")
    files = expand_paths(args.files)
    if args.store == "aws-s3":
        download(files, amazon_s3.download_file, [args.no_annex], args.workers)
    elif args.store == "azure-blob":
        download(files, azure_storage_blob.download_file, [args.no_annex], args.workers)
    else:
        raise ValueError("Unsupported --store.")
