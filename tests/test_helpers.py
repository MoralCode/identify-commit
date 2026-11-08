from pathlib import Path
import pytest
from src.identify_commit.helpers import find_high_frequency_files

# Assuming your function is in a module named file_utils.py:
# from file_utils import find_high_frequency_files


def test_find_high_frequency_files(tmp_path):
  # 1. Create files that should match the globs
  (tmp_path / "CHANGELOG.md").touch()
  (tmp_path / "Gemfile.lock").touch()
  (tmp_path / "pyproject.toml").touch()

  # 2. Create files that should NOT match
  (tmp_path / "README.md").touch()
  (tmp_path / "main.py").touch()

  # 3. Call the generator function
  found_files = list(find_high_frequency_files(tmp_path))
  found_names = {f.name for f in found_files}

  # 4. Assert only expected files are returned
  expected_names = {"CHANGELOG.md", "Gemfile.lock", "pyproject.toml"}
  assert found_names == expected_names