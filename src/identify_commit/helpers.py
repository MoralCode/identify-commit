from pathlib import Path
import os

# Directories to skip in arbitrary software projects
IGNORE_DIRS = {
    '.git', 'node_modules', '__pycache__', 'venv', '.venv', 
    'target', 'build', 'dist', '.idea', '.vscode', 'coverage'
}

def get_file_priority(path: Path) -> int:
    """Assigns a priority tier (lower number = higher frequency/importance)."""
    name = path.name.lower()
    suffix = path.suffix.lower()
    
    # Tier 1: Changelogs, lock files, core package manifests
    if (name.startswith('changelog') or 
        name.endswith('.lock') or 
        name in {'package.json', 'pyproject.toml', 'cargo.toml', 'go.mod', 'pom.xml', 'build.gradle', 'gemfile'}):
        return 1
        
    # Tier 2: Source code files
    if suffix in {'.py', '.js', '.ts', '.jsx', '.tsx', '.rs', '.go', '.java', '.cpp', '.c', '.h', '.rb', '.php', '.cs'}:
        return 2
        
    # Tier 3: Configs, environment files, and documentation
    if name.startswith('readme') or suffix in {'.md', '.yml', '.yaml', '.json', '.env', '.ini', '.cfg', '.toml'}:
        return 3
        
    # Tier 4: Everything else
    return 4

def find_high_frequency_files(path: Path):
    """
    Recursively yields all files in a software project, 
    surfacing the most likely frequently updated files first.
    """
    all_files = []
    
    # 1. Recursively traverse while skipping ignored directories
    for current_path in path.rglob('*'):
        if any(part in IGNORE_DIRS for part in current_path.parts):
            continue
        if current_path.is_file():
            all_files.append(current_path)
            
    # 2. Define a multi-level sort key:
    #    - First by priority tier (1 to 4)
    #    - Second by modification time (newest first, using negative mtime)
    def sort_key(p: Path):
        priority = get_file_priority(p)
        try:
            mtime = -p.stat().st_mtime
        except (FileNotFoundError, PermissionError):
            mtime = 0
        return (priority, mtime)
        
    all_files.sort(key=sort_key)
    
    # 3. Yield every file in order of likelihood
    yield from all_files