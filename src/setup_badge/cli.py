"""
CLI tool for generating Shields.io endpoint badges.

This module provides functionality to create and manage endpoint badges for
showcasing on README files.

The CLI command creates badges by:
1. Validating user inputs (style, colors, URL)
2. Checking out or creating the badge branch
3. Generating a JSON file with badge configuration
4. Detecting changes and pushing to remote if needed
5. Returning the endpoint badge markdown for README usage
6. Restore the original branch
"""

import configparser
import json
import os
import sys
from pathlib import Path
from typing import Any, cast

import apilgtm
import click
import git

from setup_badge import __version__


class BadgeError(Exception):
    """Custom exception for badge-related errors."""

    pass


def get_repo() -> git.Repo:
    """
    Get the Git repository object for the current working directory.

    This function retrieves the GitPython Repo object representing the
    repository in the current working directory. It's used throughout the
    module to perform git operations like branch management and commits.

    Returns:
        git.Repo: The repository object for the current directory

    Raises:
        git.exc.InvalidGitRepositoryError: If not in a git repository
    """
    return git.Repo(os.getcwd())


def checkout_branch(
    repo: git.Repo,
    branch_name: str,
    remote_name: str = "origin",
    gitconfig_name: str = "Mona Lisa",
    gitconfig_email: str = "mona.lisa@github.com",
) -> git.Head | None:
    """
    Checkout a git branch, creating it if it does not exist locally or remotely.

    Parameters:
        repo            : GitPython Repo object for the repository
        branch_name     : Branch name or commit hash to checkout
        remote_name     : Remote repository name (default: "origin")
        gitconfig_name  : Default git user name if config missing (default: "Mona Lisa")
        gitconfig_email : Default git user email if config missing (default: "mona.lisa@github.com")

    Returns:
        git.Head: The checked-out branch object on success
        None: If checkout fails or branch doesn't exist

    Raises:
        Exception: If git configuration cannot be set
    """
    # Step 1: Ensure git config exists (user.name/user.email), which is
    # essential for CI environments where these values might be missing.
    try:
        # Check if git config has user.name and user.email
        config_name = None
        config_email = None

        # Try to read existing config
        try:
            reader = repo.config_reader()
            config_name = reader.get_value("user", "name", default=None)
            config_email = reader.get_value("user", "email", default=None)
        except (configparser.NoSectionError, Exception):
            # No config file exists or section is missing - will create with defaults
            pass

        # Set defaults if missing
        with repo.config_writer() as writer:
            if config_name is None:
                writer.set_value("user", "name", gitconfig_name)
            if config_email is None:
                writer.set_value("user", "email", gitconfig_email)
    except Exception as e:
        raise Exception(f"Failed to set git configuration: {e}")

    # Step 2: Fetch remote refs to ensure fresh state
    # prune=True cleans up local refs/remotes/origin/ REFERENCES to match the server
    remote = repo.remote(name=remote_name)
    remote.fetch(prune=True)

    # Step 3: Check branch existence
    # Note: remote.refs is a collection of RemoteReference Python objects.
    # - each item in the list is an object with Git metadata and helper methods
    # - use "item".name for branch name (string) comparison
    remote_branch = f"{remote_name}/{branch_name}"
    remote_exists = any(ref.name == remote_branch for ref in remote.refs)
    local_exists = branch_name in repo.heads

    # Step 4: Detect if branch_name is a commit hash
    # Skip detection if it's already known to be a local branch (branch names also resolve as commits)
    is_commit_hash = False
    if not local_exists:
        try:
            repo.commit(branch_name)
            is_commit_hash = True
        except (ValueError, git.BadName):
            pass

    # Step 5: Handle the scenarios
    if is_commit_hash:
        print("temp 1")
        """Scenario A: Branch name is a commit hash (e.g. GitHub PR
        checkout puts HEAD in detached state).

        - create a new local branch from the current HEAD commit
        - push local branch to the remote repository (links tracking)
        """
        local_branch = repo.create_head(branch_name, str(repo.head.commit))
        remote.push(refspec=f"{local_branch.name}:{local_branch.name}", set_upstream=True)
        return cast(git.Head, local_branch.checkout())

    elif not local_exists and not remote_exists:
        print("temp 2")
        """Scenario B: Branch doesn't exist anywhere

        - create a new local branch
        - push local branch to the remote repository (links tracking)
        """
        local_branch = repo.create_head(branch_name)
        remote.push(refspec=f"{local_branch.name}:{local_branch.name}", set_upstream=True)

        return cast(git.Head, local_branch.checkout())

    elif not local_exists and remote_exists:
        print("temp 3")
        """Scenario C: Branch exists on remote but not local

        - create a new local branch from the remote branch
        - push local branch to the remote repository (links tracking)
        """
        local_branch = repo.create_head(branch_name, remote_branch)

        return cast(git.Head, local_branch.checkout())

    elif local_exists and remote_exists:
        print("temp 4")
        """Scenario D: Branch exists on both local and remote

        - check out the current local branch
        - pull from remote to sync with upstream
        """
        local_branch = repo.heads[branch_name]
        local_branch.checkout()
        repo.git.pull(remote_name, branch_name)

        return cast(git.Head, local_branch.checkout())

    elif local_exists and not remote_exists:
        print("temp 5")
        """Scenario E: Branch exists on local but not remote
        We ran remote.fetch(prune=True) in step 2.  When remote branch no longer
        exists, reference to RemoteReference object is removed.  The .git/config
        is left untouched but now: "local_branch.tracking_branch() is None"

        - check out the current local branch
        - re-define the destination branch name on the server
        """
        local_branch = repo.heads[branch_name]
        remote.push(refspec=f"{local_branch.name}:{local_branch.name}", set_upstream=True)

        return cast(git.Head, local_branch.checkout())

    else:
        raise BadgeError("unexpected branch checkout scenario")  # pragma: no cover


def check_user_inputs(
    available_badge_styles: list, badge_style: str, badge_url: str, label_color: str, message_color: str
) -> bool:
    """
    Validate user inputs for badge generation parameters.

    This function checks that all user-provided parameters are valid:
    - Label and message colors must be valid hex colors (3 or 6 digits)
    - Badge style must be one of the supported styles
    - Badge URL (if provided) must be a valid URL

    Parameters:
        available_badge_styles: List of supported badge styles
        badge_style           : Badge visual style to validate
        badge_url             : Optional clickable URL for the badge
        label_color           : Left side hex color (background)
        message_color         : Right side hex color (background)

    Returns:
        bool: True if all inputs are valid, False otherwise
    """
    if all(
        [
            check_hex_color(label_color),
            check_hex_color(message_color),
            badge_style in available_badge_styles,
            True if not badge_url else apilgtm.evaluate_url(badge_url),
        ]
    ):
        return True
    else:
        return False


def check_hex_color(hex_color: str) -> bool:
    """
    Validate that a string is a valid hex color code.

    This function checks if the input is a valid hexadecimal color code:
    - Can be 3-digit (e.g., "f0a") or 6-digit (e.g., "ff00aa")
    - Can optionally start with "#" (which is stripped)
    - Must contain only valid hex characters (0-9, a-f, A-F)

    Parameters:
        hex_color: Color string to validate (with or without "#")

    Returns:
        bool: True if the string is a valid hex color, False otherwise
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) not in [3, 6]:
        return False
    try:
        int(hex_color, 16)
        return True
    except ValueError:
        return False


def create_badge_dict(badge_style: str, label: str, label_color: str, message: str, message_color: str) -> dict:
    """
    Create a dictionary conforming to Shields.io endpoint badge schema.

    This function generates a properly structured dictionary that can be
    serialized to JSON and used by Shields.io to render a badge. The
    dictionary includes all required fields for the badge specification.

    Parameters:
        badge_style  : Badge visual style (flat, flat-square, plastic, for-the-badge, social)
        label        : Text displayed on the left side of the badge
        label_color  : Hex color for the left side background
        message      : Text displayed on the right side of the badge
        message_color: Hex color for the right side background

    Returns:
        dict: A dictionary with keys: schemaVersion, style, label, labelColor, message, color
    """
    badge_dict = {
        "schemaVersion": 1,
        "style": badge_style,
        "label": label,
        "labelColor": label_color,
        "message": message,
        "color": message_color,
    }
    return badge_dict


def create_badge_json(badge_dict: dict | Any, badge_name: str) -> bool:
    """
    Create a badge JSON file in the badges directory.

    This function writes a badge configuration dictionary to a JSON file
    in the "badges" subdirectory. The directory is created if it doesn't
    exist. The JSON is formatted with indentation for readability.

    Parameters:
        badge_dict: Dictionary containing badge configuration (schemaVersion, style, label, etc.)
        badge_name: Name for the badge file (without extension, e.g., "my-badge")

    Returns:
        bool: True if file was created successfully, False otherwise

    Side effects:
    - Creates "badges/" directory if it doesn't exist
    - Writes JSON file to "badges/{badge_name}.json"
    """
    badge_file_dst = f"badges/{badge_name}.json"

    if isinstance(badge_dict, dict):
        badge_path = Path("badges")
        badge_path.mkdir(parents=True, exist_ok=True)

        with open(badge_file_dst, "w") as json_file:
            json.dump(badge_dict, json_file, indent=2)
            json_file.write("\n")

        return True
    else:
        return False


def check_badge_changes(repo: git.Repo, badge_name: str) -> bool:
    """
    Check if the badge file has uncommitted changes.

    This function detects whether a badge file needs to be committed by
    checking both untracked files and modified files in the git repository.
    It's used to determine if the badge generation process should proceed
    with staging, committing, and pushing changes.

    Parameters:
        repo      : GitPython Repo object for the repository
        badge_name: Name of the badge file (without extension)

    Returns:
        bool: True if changes are detected, False if the file is unchanged

    The function checks:
    - Whether badges/{badge_name}.json is in untracked files
    - Whether the file has been modified since the last commit (git diff)
    """
    if any(
        [
            f"badges/{badge_name}.json" in repo.untracked_files,
            len(repo.git.diff("HEAD", f"badges/{badge_name}.json")) > 0,
        ]
    ):
        return True
    else:
        return False


def push_changes(repo: git.Repo, remote_name: str, badge_branch: str, badge_name: str) -> str | None:
    """
    Stage, commit, and push badge changes to the remote repository.

    This function performs the complete git workflow for pushing badge
    updates: staging the file, creating a commit with a descriptive message,
    and pushing to the remote branch.

    Parameters:
        repo        : GitPython Repo object for the repository
        remote_name : Remote repository name (default: "origin")
        badge_branch: Branch name where badge should be pushed
        badge_name  : Name of the badge file (without extension)

    Returns:
        str | None: The commit hash (first 7 chars) on success, None on failure

    Side effects:
    - Stages badges/{badge_name}.json
    - Creates a commit with message indicating the branch
    - Pushes to remote branch with upstream tracking

    The commit message format: "add/update to branch ({badge_branch})"
    """
    try:
        repo.index.add([f"badges/{badge_name}.json"])
        repo.index.write()
        message = f"add/update to branch ({badge_branch})"
        commit = repo.index.commit(message)
        commit_hash = f"{commit.hexsha}"
        repo.git.push("--set-upstream", remote_name, badge_branch)

        return commit_hash

    except Exception as e:
        print(f"❌ {e}")
        return None  # pragma: no cover


def create_shieldsio_endpoint_badge(repo: git.Repo, badge_branch: str, badge_name: str, badge_url: str) -> str:
    """
    Generate a Shields.io endpoint badge markdown string.

    This function constructs a Shields.io endpoint badge URL that points
    to the badge JSON file in the repository. It supports two formats:
    - Plain image badge: `![badge_name](https://img.shields.io/endpoint?url=...)`
    - Clickable badge: `[![badge_name](https://img.shields.io/endpoint?url=...)](badge_url)`

    The function extracts the owner and repository name from the remote URL,
    handling both SSH (git@github.com:) and HTTPS (https://github.com/) formats.

    Parameters:
        repo        : GitPython Repo object for the repository
        badge_branch: Branch name where badge JSON is stored
        badge_name  : Name of the badge file (without extension)
        badge_url   : Optional URL the badge should link to

    Returns:
        str: Markdown string for the badge that can be added to README files

    Example return value (without URL):
        "![badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/owner/repo/refs/heads/badges/badges/badge.json)"

    Example return value (with URL):
        "[![badge](https://img.shields.io/endpoint?url=...)](https://example.com)"
    """
    shields_io = "https://img.shields.io/endpoint"
    raw_github = "https://raw.githubusercontent.com"
    repo_remotes_url = repo.remotes.origin.url
    owner_repo = (
        "/".join(repo_remotes_url.rsplit("/", 2)[-2:])
        .replace(".git", "")
        .replace("git@github.com:", "")
        .replace("https://github.com/", "")
    )

    json_endpoint = f"{raw_github}/{owner_repo}/refs/heads/{badge_branch}/badges/{badge_name}.json"
    if badge_url:
        eb = f"[![{badge_name}]({shields_io}?url={json_endpoint})]({badge_url})"
    else:
        eb = f"![{badge_name}]({shields_io}?url={json_endpoint})"

    return eb


@click.command()
@click.option("--badge-name", default="badge", help="default: badge")
@click.option("--badge-branch", default="badges", help="default: badges")
@click.option("--badge-url", default="", help="default: ''")
@click.option("--badge-style", default="flat", help="default: flat (flat, flat-square, plastic, for-the-badge, social)")
@click.option("--label", default="demo", help="default: demo (badge left side text)")
@click.option("--label-color", default="2e2e2e", help="default: 2e2e2e (badge left side hex color)")
@click.option("--message", default="no status", help="default: no status (badge right side text)")
@click.option("--message-color", default="2986CC", help="default: 2986CC (badge right side hex color)")
@click.option("--remote-name", default="origin", help="default: origin")
@click.option("--gitconfig-name", default="Mona Lisa", help="default: Mona Lisa")
@click.option("--gitconfig-email", default="mona.lisa@github.com", help="default: mona.lisa@github.com")
@click.version_option(version=__version__)
def main(
    badge_branch,
    badge_name,
    remote_name,
    badge_style,
    badge_url,
    label,
    label_color,
    message,
    message_color,
    gitconfig_name,
    gitconfig_email,
) -> None:
    """CLI command to generate and deploy Shields.io endpoint badges.

    This command creates a badge configuration, commits it to a designated
    branch, and generates the endpoint badge URL for use in README files.
    """
    available_badge_styles = ["flat", "flat-square", "plastic", "for-the-badge", "social"]

    print(f"🚀 Starting to create a badge ({badge_name}.json) on branch ({badge_branch})...\n")

    try:
        repo = get_repo()
        # Validate user inputs before proceeding
        if check_user_inputs(available_badge_styles, badge_style, badge_url, label_color, message_color):
            print("✅ validated inputs from command line options")

            # Save original branch to restore later
            original_branch = repo.active_branch.name

            # Checkout the badge branch (create if needed)
            if checkout_branch(repo, badge_branch, remote_name, gitconfig_name, gitconfig_email):
                print(f"✅ checkout local branch ({badge_branch})")

                # Generate badge configuration and write to JSON file
                badge_dict = create_badge_dict(badge_style, label, label_color, message, message_color)
                if create_badge_json(badge_dict, badge_name):
                    print(f"✅ created badges/{badge_name}.json")

                    # Check if badge file has changes and push if needed
                    if check_badge_changes(repo, badge_name):
                        print(f"✅ found changes ready to stage, commit, and push to {remote_name}")

                        commit_hash = push_changes(repo, remote_name, badge_branch, badge_name)
                        if commit_hash is not None:
                            print(f"✅ pushed commit ({commit_hash[:7]}) to remote branch ({badge_branch})")

                        else:
                            raise BadgeError(f"failed to push changes to {remote_name}")

                        # Generate and display the endpoint badge for README
                        endpoint_badge = create_shieldsio_endpoint_badge(repo, badge_branch, badge_name, badge_url)
                        print(f"\n🎉 Endpoint Badge: {endpoint_badge}")

                        # Restore original branch
                        local_branch = repo.heads[original_branch]
                        local_branch.checkout()
                        print(f"🤩 Branch restored to original active branch: {original_branch}")

                    else:
                        print("✅ found no changes (current branch is up to date)")

                        # No changes, just restore original branch
                        local_branch = repo.heads[original_branch]
                        local_branch.checkout()
                        print(f"🤩 Branch restored to original active branch: {original_branch}")

                else:
                    raise BadgeError(f"failed to create {badge_name}.json")

            else:
                raise BadgeError(f"failed to checkout branch {badge_branch}")

        else:
            raise BadgeError("one or more of your inputs failed validations")

    except Exception as err:
        print(f"❌ Exception: {err}") if err else print("❌ Unexpected Exception Error")
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
