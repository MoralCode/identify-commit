from pathlib import Path

def find_high_frequency_files(path: Path):
    """ identify files that may be more frequently updated in a folder """

    glob_strings = ['CHANGELOG.md', "*.lock", "*.toml"]

    for glob_str in glob_strings:
        yield from path.glob(glob_str)

