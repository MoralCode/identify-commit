import argparse
import os
import sys
import tempfile
import pygit2
import logging
from pathlib import Path
from .helpers import find_high_frequency_files

logger = logging.getLogger(__name__)

# how many commits the user is willing to manually check
# AKA how many commits should we narrow the search down to before considering the result acceptable
MANUAL_CHECK_THRESHOLD = 5
MAX_COMMIT_DISPLAY = 10

def print_matches(logger, commits):
    commits = list(commits)
    count = len(commits)
    msg = f"Found {len(commits)}"
    if count > MAX_COMMIT_DISPLAY:
        msg += f" (truncated to {MAX_COMMIT_DISPLAY})"
        commits = commits[:MAX_COMMIT_DISPLAY]
    msg += " matching commits:"
    logger.debug(msg)
    logger.debug(commits)

def filter_commits_for_blob(repo:pygit2.Repo, commits:list[pygit2.Walker], target_blob_id):
    matching_commits = []
    # 3. Replicates: xargs with ls-tree checking for blob match
    for commit in commits:
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
                matching_commits.append(commit)
                logger.debug(str(commit))
        except Exception:
            continue

    return matching_commits


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

    logging.basicConfig( level=args.level.upper() )
    logger.info( 'Logging now setup.' )

    local_dir = Path(args.local_dir)

    if not Path.exists(local_dir):
        raise FileNotFoundError(f"Local dir not found: {local_dir}")

    # make temp dir
    temp_dir = Path(tempfile.mkdtemp())

    repo_url = args.repo_url
    local_dir = Path(args.local_dir)

    # clone repo
    logger.info(f"Cloning repository from {repo_url}...")
    repo = pygit2.clone_repository(repo_url, temp_dir, bare=True)
    # the clone happens directly into temp_dir per observation

    # get commits list
    # 2. Replicates: git rev-list --all traversal
    logger.info("Walking all commits (--all)...")
    walker = repo.walk(repo.head.target, pygit2.enums.SortMode.TIME)

    # Push all references (branches, tags, remotes) into the walker to cover --all
    for refname in repo.references:
        try:
            target = repo.lookup_reference(refname).target
            if isinstance(target, pygit2.Oid):
                walker.push(target)
        except Exception:
            pass
    # start out assuming every commit is a match
    matching_commits = list(walker)
    
    # copy all files from local dir into the repo, with overwrite


    # pick a file with high frequency updates
    for local_file_path in find_high_frequency_files(local_dir):
        logger.debug(f"Evaluating file: {local_file_path}")
        # relative_filepath = local_file_path.relative_to(local_dir)
        # logger.debug(relative_filepath)
        # in_repo_filepath = temp_dir.joinpath(relative_filepath)
        # logger.debug(in_repo_filepath)

        # copy the file to the current repo
        # apparrently not needed as the hashing works without the phyle being in the repo????
        
        # get its hash
        # 1. Replicates: git hash-object <file>
        target_blob_id = pygit2.hashfile(local_file_path)
        logger.debug(
            f"Target blob OID (hash-object):"
            f" {target_blob_id} ({str(target_blob_id)})"
        )

        # filter commits list by blob id
        matching_commits = filter_commits_for_blob(repo, matching_commits, target_blob_id)
        print_matches(logger, matching_commits)

        # if 0: pick another
        if len(matching_commits) == 0:
            raise NotImplementedError("We ran out of viable commits to check before finding a definitive match. One of the input files is not a byte-for-byte match for any of its versions in this repo")
        elif len(matching_commits) <= MANUAL_CHECK_THRESHOLD:
            logger.info(str(matching_commits[0]))
            sys.exit(0)
            # if 1: return
        else:
            # if we have too many commits, repeat the loop to bring in another file and keep filtering.
            pass
        
    #cleanup temp dir
    temp_dir.unlink()
