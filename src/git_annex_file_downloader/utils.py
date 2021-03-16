import functools
import hashlib
import shlex
import subprocess
from concurrent import futures
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional, Tuple, TypeVar, Union


def get_file_size_from_key(annex_file_key: str) -> int:
    return int(annex_file_key.split("-")[1][1:])  # SHA256E-s1024--81a9ef8...


def git_annex_lookupkey(file_path: Path) -> str:
    command = shlex.split(f"git annex lookupkey {file_path}")
    result = subprocess.run(command, capture_output=True)
    return result.stdout.decode().strip("\n")


def lookup_key(symlink_path: Path, subfolders: bool = False) -> str:
    annex_key = symlink_path.resolve().name
    if subfolders:
        key_checksum = md5sum(annex_key.encode())
        subdirs = f"{key_checksum[:3]}/{key_checksum[3:6]}"
        return f"{subdirs}/{annex_key}"
    return annex_key


def needs_download(file_path: Path, file_size: int) -> bool:
    if file_path.resolve().is_file():
        if file_path.stat().st_size == file_size:
            return False
    return True


def mkdirs(file_path: Path):
    """Create parent directories and ignore if they already exist."""
    file_path.parent.mkdir(parents=True, exist_ok=True)


T = TypeVar("T")
U = TypeVar("U")


def raise_if_none(func: Callable[..., Optional[U]]) -> Callable[..., U]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result is None:
            raise ValueError("Got an unexpected 'None'")
        return result
    return wrapper


def run_command(
    command: str, stdin: Optional[bytes] = None, stdout=None
) -> Optional[str]:
    """Optionally use a writable file object as stdout."""
    if stdout is None:
        stdout = subprocess.PIPE
    command_line = shlex.split(command)
    result: subprocess.CompletedProcess = subprocess.run(
        command_line, input=stdin, stdout=stdout, stderr=subprocess.PIPE
    )
    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        print(result.stderr)
        print(stdout)
        exit()
    if stdout == subprocess.PIPE:
        output = result.stdout.decode()
        return output


def run_command_chain(commands: List[str]) -> str:
    previous_output = None
    for command in commands:
        previous_output = run_command(command, stdin=previous_output).encode()
    return previous_output.decode()


def map_parallel(
    function: Callable[[U], T],
    iterable: Iterable[U],
    singleton: Any = None,
    workers: int = 8,
) -> Iterable[Tuple[Union[str, T], U]]:
    with futures.ThreadPoolExecutor(max_workers=workers) as executor:
        if singleton is not None:
            jobs = {
                executor.submit(function, param, singleton): param
                for param in iterable
            }
        else:
            jobs = {executor.submit(function, param): param for param in iterable}
        for job in futures.as_completed(jobs):
            exception = job.exception()
            result = str(exception) if exception is not None else job.result()
            yield result, jobs[job]


def md5sum(content: bytes) -> str:
    hash_md5 = hashlib.md5()
    hash_md5.update(content)
    return hash_md5.hexdigest()
