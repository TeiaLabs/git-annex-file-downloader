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


def expand_paths_from_json(paths: Iterable[Path], json_path: Path | str) -> Iterable[Path]:
    mapping = utils.load_json(json_path)
    # all_available_paths = [Path(k) for k in mapping.keys()]
    all_available_paths: list[str] = list(mapping.keys())
    expanded_paths = []
    for p in paths:
        for available_path in all_available_paths:
            if available_path.startswith(str(p)):
                expanded_paths.append(available_path)
    return expanded_paths


def main():
    args = cli_args.get_args()
    if args.no_annex:
        logger.info("Working without git-annex")
        files = expand_paths_from_json(args.files, "large_files.json")
    else:
        files = expand_paths(args.files)
    logger.debug(f"From {args.store}.")
    if args.store == "aws-s3":
        download(files, amazon_s3.download_file, [args.no_annex], args.workers)
    elif args.store == "azure-blob":
        download(files, azure_storage_blob.download_file, [args.no_annex], args.workers)
    else:
        raise ValueError("Unsupported --store.")
