# Identify Commit

A command-line tool written in Python that finds the exact historical git commit matching a directory of local files. It uses **`pygit2`** (`libgit2`) to efficiently scan repository history, filter commits by file blob hashes iteratively, and pinpoint the exact commit your files came from.

---

## Features

* **In-Memory Git Operations:** Leverages `libgit2` for fast history traversal without spawning external `git` shell processes.
* **Iterative Refinement:** Automatically cycles through high-frequency update files (like `CHANGELOG.md`, `*.lock`, `*.toml`) to narrow down candidate commits quickly.
* **Bare Clone Efficiency:** Clones repos as bare repositories into temporary workspaces, cleaning up automatically after execution.

---

## Prerequisites

* Python 3.10+
* [uv](https://github.com/astral-sh/uv) (recommended) or `pip`

---

## Installation

1. Clone or download this project workspace.
2. Install dependencies:
```bash
uv pip install pygit2
# or using standard pip:
pip install pygit2

```



---

## Usage

Run the tool from your command line by passing the repository URL and the path to your local project directory:

```bash
uv run identify-commit <repo-url> <path/to/local-dir> --level <log-level>

```

### Example

```bash
uv run identify-commit https://github.com/Alamofire/Alamofire ./Alamofire/ --level debug

```

### Command-Line Arguments

| Argument    | Description                                                 | Default    |
| ----------- | ----------------------------------------------------------- | ---------- |
| `repo_url`  | URL to the target git repository the files originated from. | *Required* |
| `local_dir` | Path to the directory containing your local file snapshot.  | *Required* |
| `--level`   | Logging level (`debug`, `info`, `warning`, `error`).        | `warning`  |

---

## How It Works

1. **Bare Clone:** Clones the remote repository into a temporary directory using a bare configuration for maximum speed.
2. **Commit Traversal:** Builds a complete commit list covering all branches, tags, and remotes (`--all`).
3. **Blob Hashing:** Computes the local Git blob hash (`hash-object`) for files identified by `find_high_frequency_files` (e.g., `CHANGELOG.md`, `Gemfile.lock`).
4. **Iterative Filtering:** Filters the candidate commit list file-by-file until a single definitive matching commit is isolated, printing the result.