import argparse
import os
import tempfile
import pygit2
import logging
from pathlib import Path
from helpers import find_high_frequency_files

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Find commits containing a specific local file blob using libgit2."
        )
    )
    parser.add_argument("repo_url", help="URL to the git repository the files came from")
    parser.add_argument(
        "local_dir", help="Path to the directory of the local files"
    )
    parser.add_argument('--level',
                    default='warning',
                    help='Provide logging level. Example --loglevel debug, default=warning' )

    args = parser.parse_args()

    logger.basicConfig( level=args.loglevel.upper() )
    logger.info( 'Logging now setup.' )

    local_dir = args.local_dir

    if not Path.exists(local_dir):
        raise FileNotFoundError(f"Local dir not found: {local_dir}")

    # make temp dir
    temp_dir = tempfile.mkdtemp()

    repo_url = args.repo_url
    local_dir = args.local_dir

    # clone repo
    logger.info(f"Cloning repository from {repo_url}...")
    # Clone as bare repository for fast history traversal
    repo = pygit2.clone_repository(repo_url, temp_dir, bare=True)
    
    # copy all files from local dir into the repo, with overwrite


    # pick a file with high frequency updates
    for local_file_path in find_high_frequency_files(local_dir):
        # get its hash
        # 1. Replicates: git hash-object <file>
        target_blob_id = pygit2.hashfile(local_file_path)
        print(
            f"Target blob OID (hash-object):"
            f" {target_blob_id} ({target_blob_id.hex})"
        )

        # search commits with that file hash

        # 2. Replicates: git rev-list --all traversal
        print("Walking all commits (--all)...")
        walker = repo.walk(repo.head.target, pygit2.enums.SortMode.TIME)

        # Push all references (branches, tags, remotes) into the walker to cover --all
        for refname in repo.references:
            try:
                target = repo.lookup_reference(refname).target
                if isinstance(target, pygit2.Oid):
                    walker.push(target)
            except Exception:
                pass

        matching_commits = []

        # 3. Replicates: xargs with ls-tree checking for blob match
        for commit in walker:
            try:
                # tree.peel(pygit2.Tree, path) or walking the tree recursively
                # To efficiently search the tree, we can walk the commit's tree entries
                found = False
                stack = [(commit.tree, "")]
                while stack:
                    current_tree, current_path = stack.pop()
                    for entry in current_tree:
                        if entry.id == target_blob_id:
                            found = True
                            break
                        # If it's a subdirectory, push it to stack for recursive search
                        elif entry.type_str == "tree":
                            stack.append((repo[entry.id], entry.name))
                    if found:
                        break

                if found:
                    matching_commits.append(commit.hex)
                    print(commit.hex)
            except Exception:
                continue

        return matching_commits




    # if 0: pick another
    # if 1: return
    # if 2+: add commits to a set and filter on the next iteration to narrow down
        
    #cleanup temp dir
    import shutil
    shutil.rmtree(temp_dir)
