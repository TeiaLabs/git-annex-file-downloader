from typing import List

import setuptools


def read_multiline_as_list(file_path: str) -> List[str]:
    with open(file_path) as fh:
        contents = fh.read().split("\n")
        if contents[-1] == "":
            contents.pop()
        return contents


with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = read_multiline_as_list("requirements.txt")

# classifiers = read_multiline_as_list("classifiers.txt")

description = (
    "Python alternative to download git annexed files programatically from "
    "supported special remotes without installing git-annex."
)

setuptools.setup(
    name="git-annex-file-downloader",
    version="1.0.0",
    author="Nei Cardoso de Oliveira Neto @ Teia Labs",
    author_email="nei@teialabs.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TeiaLabs/git-annex-file-downloader/",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    # classifiers=classifiers,
    keywords='git annex special remote, s3, azure blob storage, python bindings',
    entry_points={
        'console_scripts': [
            'gadown=git_annex_file_downloader.file_downloader:main',
        ],
    },
    python_requires=">=3.8, <3.9",
    install_requires=requirements,
)
