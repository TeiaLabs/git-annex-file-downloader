import json
import sys
from pathlib import Path

from . import utils


def save_json(obj, path, indent: int = 2, **kwargs):
    try:
        with open(path, "w") as file_handler:
            json.dump(obj, file_handler, indent=indent, **kwargs)
    except PermissionError as e:
        if path.is_symlink():
            msg = f"\tFor safety reasons, {path!r} is read-only.\n"
            msg += f"\tRun 'git annex unlock {path}' to enable write-access."
            print(f"{e.__class__.__name__}:\n", msg, file=sys.stderr)
            exit(403)
        else:
            raise e


def main():
    git_annexed_files = utils.run_command("git annex find").split("\n")
    git_annexed_files = filter(bool, git_annexed_files)
    git_annexed_paths = list(map(Path, git_annexed_files))
    files_keys = map(utils.git_annex_lookupkey, git_annexed_paths)
    mapping_ = {
        str(file_path): file_key
        for file_path, file_key in zip(git_annexed_paths, files_keys)
    }
    save_json(mapping_, "large_files.json")


if __name__ == "__main__":
    main()
