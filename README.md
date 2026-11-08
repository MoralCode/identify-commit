# Identify Commit

A command-line tool written in Python that helps identify an exact historical git commit that matches a directory of local files.

This is useful for:
- identifying the commit where files from another repo came from when its not cited (may not be that reliable as the method relies on having many files)
- taking a folder from a git repo (like a DIY submodule) and helping convert it to an actual submodule
- probably more, the usecase is fairly niche though

It uses **`pygit2`** (`libgit2`) to efficiently scan repository history and filter commits by file blob hashes iteratively to help you pinpoint the exact commit your files came from.


## Preconditions
This repo requires that:
- you know what repo the files are from, and just want help identifying the point in history they were copied from
- you have a directory of at least one file that is byte-for-byte identical to at least one version of that same file in your target repo

## Limitations

Currently this repo only looks for specific files (`CHANGELOG.md`, `*.lock`, `*.toml`) that are likely to be updated at high frequency (for faster narrowing down of options).

Support for arbitrary files is coming soon/relatively easy to add (only one small function needs to change)


## Dependencies

* Python 3.10+
* [uv](https://github.com/astral-sh/uv) (recommended) or `pip`


## Installation

1. Clone or download this project workspace.
2. `uv run identify-commit --help` for the available syntax


## Usage

Run the tool from your command line by passing the repository URL and the path to a local directory containing the files that you want:

```bash
uv run identify-commit <repo-url> <path/to/local-dir>
```

## How It Works

1. **Bare Clone:** Clones the remote repository into a temporary directory using a bare configuration for maximum speed.
2. **Commit Traversal:** Builds a complete commit list covering all branches, tags, and remotes.
3. **Blob Hashing:** iterates through files, high frequency updates first, computes the local Git blob hash (`hash-object`) of each.
4. **Iterative Filtering:** Filters the candidate commit list file-by-file using the blob hashes until a small (<10 by default) list of matching commit is isolated.
5. **Output** These candidate commits ar printed so you can check to see which one is likely to be the one you want.