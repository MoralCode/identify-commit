import argparse
import os
import tempfile
import pygit2


def find_commits_with_blob(repo_url, local_file_path):
  if not os.path.exists(local_file_path):
    raise FileNotFoundError(f"Local file not found: {local_file_path}")

  temp_dir = tempfile.mkdtemp()
  try:
    print(f"Cloning repository from {repo_url}...")
    # Clone as bare repository for fast history traversal
    repo = pygit2.clone_repository(repo_url, temp_dir, bare=True)

    # 1. Replicates: git hash-object <file>
    target_blob_id = pygit2.hashfile(local_file_path)
    print(
        f"Target blob OID (hash-object):"
        f" {target_blob_id} ({target_blob_id.hex})"
    )

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
          print(commit.hex)  # Prints the commit hash matching your echo {}
      except Exception:
        continue

    return matching_commits
  finally:
    import shutil

    shutil.rmtree(temp_dir)

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

  args = parser.parse_args()
  find_commits_with_blob(args.repo_url, args.local_dir)