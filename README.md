# git-annex-file-downloader

Python alternative to download git annexed files programatically from supported special remotes without installing git-annex.

## Installation

```bash
pip install git+https://github.com/TeiaLabs/git-annex-file-downloader.git@master
```

## Developer installation

`git clone git@github.com:TeiaLabs/git-annex-file-downloader.git`

`pip install -e ./git-annex-file-downloader/`

## Usage

`gadown --help` is your friend.

### Single file

`gadown --files some-big-file.dat`

### All files under a directory (with parallelism)

`gadown --files resources/ --workers 4`

### Several specific files

`gadown --files file1 file2 some-folder/file3 file4 --workers 2`

### Files from another repo

```bash
cd the-other-repo
# generate a JSON that maps paths to annex keys
python -m git_annex_file_downloader.export_keys
# move it to the directory where you intend to use git-annex-file-downloader
mv large_files.json /some-dir/
# grab the encryption cipher from a git-annex metadata file
git show git-annex:remote.log | grep special-remote-name
# copy just the cipher
export cipher=<paste your cipher>
cd /some-dir/
gadown --files data/database.sqlite --no-annex
```
