#!/usr/bin/env python

"""
Purpose: Generate an endpoint badge to showcase on README
"""

import json
import os
from pathlib import Path

import click
import git
import validators

from setup_badge import __version__


def get_repo():
    """
    Get repo class object

    Return: repo class object 'git.repo.base.Repo'
    """
    return git.Repo(os.getcwd())


def checkout_branch(repo, remote_name, badge_branch, gitconfig_name, gitconfig_email):
    """
    Checkout a git branch

    Parameter(s):
    repo           : repo class object 'git.repo.base.Repo'
    remote_name    : remote name (e.g. origin)
    badge_branch   : badge branch name (e.g. badges)
    gitconfig_name : git config user name
    gitconfig_email: git config user email

    Return: branch object '<class 'git.refs.head.Head'>' or None
    """
    try:
        # Specify git config user info and how to reconcile divergent branches on pull
        reader = repo.config_reader()
        name = reader.get_value('user', 'name', default='runner')
        email = reader.get_value('user', 'name', default='runner@github.com')
        if any([name == 'runner', email == 'runner@github.com']):
            with repo.config_writer() as writer:
                writer.set_value('user', 'name', gitconfig_name)
                writer.set_value('user', 'name', gitconfig_email)
                writer.set_value('pull', 'rebase', 'false')

        # Without fetch with prune, local may not realize that upstream is gone
        origin = repo.remote(name=remote_name)
        origin.fetch(prune=True)

        if repo.head.is_detached:
            # scenario: on pull request (pull/XX/merge), head is in detached state
            local_branch = repo.create_head(badge_branch, repo.head.commit)
            origin.push(local_branch.name, set_upstream=True)

        else:
            if any(ref.name == f'{remote_name}/{badge_branch}' for ref in origin.refs):
                if badge_branch not in repo.heads:
                    # scenario: badge branch exists in remote but not in local
                    local_branch = repo.create_head(badge_branch, f'{remote_name}/{badge_branch}')
                    origin.push(local_branch.name, set_upstream=True)

                else:
                    if repo.is_dirty(untracked_files=True):
                        # scenario: badge branch exists in both local and remote (with local changes)
                        raise Exception('Stage and commit your local changes and try again')

                    remote = repo.remotes.origin
                    remote.pull()
                    local_branch = repo.heads[badge_branch]

            else:
                if repo.active_branch.name == badge_branch:
                    # scenario: badge branch (active branch) exists in local but not in remote
                    local_branch = repo.heads[badge_branch]

                else:
                    local_branch = repo.create_head(badge_branch, repo.active_branch.name)

                origin.push(local_branch.name, set_upstream=True)

        return local_branch.checkout()

    except Exception as e:
        print(f'❌ {e}')
        return None


def check_user_inputs(available_badge_styles, badge_style, badge_url, label_color, message_color):
    """
    Check user inputs

    Parameter(s):
    available_badge_styles: a list of available badge styles
    badge_style           : badge appearance
    badge_url             : badge clickable url
    label_color           : badge background hex color (left side)
    message_color         : badge background hex color (right side)

    Return: boolean
    """
    if all([
            check_hex_color(label_color),
            check_hex_color(message_color),
            badge_style in available_badge_styles,
            True if not badge_url else validators.url(badge_url)
            ]):
        return True
    else:
        return False


def check_hex_color(hex_color):
    """
    Check if the hex color variable is valid

    Parameter(s):
    hex_color: hex color for label-color or message-color

    Return: boolean
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) not in [3, 6]:
        return False
    try:
        int(hex_color, 16)
        return True
    except ValueError:
        return False


def create_badge_dict(badge_style, label, label_color, message, message_color):
    """
    Create python dictionary for json file

    Parameter(s):
    badge_style  : badge appearance
    label        : badge text (left side)
    label_color  : badge background hex color (left side)
    message      : badge text (right side)
    message_color: badge background hex color (right side)

    Return: python dictionary
    """
    badge_dict = {'schemaVersion': 1, 'style': badge_style, 'label': label, 'labelColor': label_color,
                  'message': message, 'color': message_color}
    return badge_dict


def create_badge_json(badge_dict, badge_name):
    """
    Create badge json files from python dictionary

    Parameter(s):
    badge_dict: a python dictionary in shields.io endpoint badge schema
    badge_name: badge filename (e.g. badge)

    Return: boolean
    """
    badge_file_dst = f'badges/{badge_name}.json'

    if isinstance(badge_dict, dict):
        badge_path = Path('badges')
        badge_path.mkdir(parents=True, exist_ok=True)

        with open(badge_file_dst, 'w') as json_file:
            json.dump(badge_dict, json_file, indent=2)
            json_file.write("\n")

        return True
    else:
        return False


def check_badge_changes(repo, badge_name):
    """
    Check any badge changes

    Parameter(s):
    repo      : repo class object 'git.repo.base.Repo'
    badge_name: badge filename (e.g. badge)

    Return: boolean
    """
    if any([
            f'badges/{badge_name}.json' in repo.untracked_files,
            len(repo.git.diff('HEAD', f'badges/{badge_name}.json')) > 0,
            ]):
        return True
    else:
        return False


def push_changes(repo, remote_name, badge_branch, badge_name, msg_suffix):
    """
    Stage and write commits, and push to remote

    Parameter(s):
    repo        : repo class object 'git.repo.base.Repo'
    remote_name : remote name (e.g. origin)
    badge_branch: badge branch name (e.g. badges)
    badge_name  : badge filename (e.g. badge)
    msg_suffix  : suffix to append to commit message

    Return: commit hash or None
    """
    try:
        repo.index.add([f'badges/{badge_name}.json'])
        repo.index.write()
        message = f'add/update to branch ({badge_branch}) {msg_suffix}'
        commit = repo.index.commit(message)
        commit_hash = f'{commit.hexsha}'
        repo.git.push('--set-upstream', remote_name, badge_branch)

        return commit_hash

    except Exception as e:
        print(f'❌ {e}')
        return None


def create_shieldsio_endpoint_badge(repo, badge_branch, badge_name, badge_url):
    """
    Create Shields.io Endpoint Badge

    Parameter(s):
    repo        : repo class object 'git.repo.base.Repo'
    badge_name  : badge filename (e.g. badge)
    badge_branch: badge branch name (e.g. badges)
    badge_url   : badge clickable url

    Return: Shields.io endpoint badge
    """
    shields_io = 'https://img.shields.io/endpoint'
    raw_github = 'https://raw.githubusercontent.com'
    repo_remotes_url = repo.remotes.origin.url
    owner_repo = '/'.join(repo_remotes_url.rsplit('/', 2)[-2:]).replace('.git', '').replace('git@github.com:', '')
    json_endpoint = f'{raw_github}/{owner_repo}/refs/heads/{badge_branch}/badges/{badge_name}.json'
    if badge_url:
        eb = f'[![{badge_name}]({shields_io}?url={json_endpoint})]({badge_url})'
    else:
        eb = f'![{badge_name}]({shields_io}?url={json_endpoint})'

    return eb


def cicleanup(repo, remote_name, badge_branch):
    """
    Cleanup - delete the remote badge branch if triggered by 'coverage run'

    Parameter(s):
    repo        : repo class object 'git.repo.base.Repo'
    remote_name : remote name (e.g. origin)
    badge_branch: badge branch name (e.g. badges)
    """
    try:
        origin = repo.remote(remote_name)
        origin.push(refspec=f':{badge_branch}')
        return True

    except Exception as e:
        print(f'❌ {e}')
        return False


@click.command()
@click.option('--badge-name', default='badge', help='default: badge')
@click.option('--badge-branch', default='badges', help='default: badges')
@click.option('--badge-url', default='', help="default: ''")
@click.option('--badge-style', default='flat', help='default: flat (flat, flat-square, plastic, for-the-badge, social)')
@click.option('--label', default='demo', help='default: demo (badge left side text)')
@click.option('--label-color', default='2e2e2e', help='default: 2e2e2e (badge left side hex color)')
@click.option('--message', default='no status', help='default: no status (badge right side text)')
@click.option('--message-color', default='2986CC', help='default: 2986CC (badge right side hex color)')
@click.option('--remote-name', default='origin', help='default: origin')
@click.option('--gitconfig-name', default='Mona Lisa', help='default: Mona Lisa')
@click.option('--gitconfig-email', default='mona.lisa@github.com', help='default: mona.lisa@github.com')
@click.version_option(version=__version__)
def main(badge_branch, badge_name, remote_name, badge_style, badge_url, label, label_color, message,
         message_color, gitconfig_name, gitconfig_email):
    repo = get_repo()
    available_badge_styles = ['flat', 'flat-square', 'plastic', 'for-the-badge', 'social']

    print(f'🚀 Starting to create a badge ({badge_name}.json) on branch ({badge_branch})...\n')
    if check_user_inputs(available_badge_styles, badge_style, badge_url, label_color, message_color):
        print('✅ validated inputs from command line options')

        if checkout_branch(repo, remote_name, badge_branch, gitconfig_name, gitconfig_email) is not None:
            print(f'✅ checkout local branch ({badge_branch})')
            repo.git.pull()

            badge_dict = create_badge_dict(badge_style, label, label_color, message, message_color)
            if create_badge_json(badge_dict, badge_name):
                print(f'✅ created badges/{badge_name}.json')

                if check_badge_changes(repo, badge_name):
                    print(f'✅ found changes ready to stage, commit, and push to {remote_name}')

                    msg_suffix = '[CI - Testing]' if 'COVERAGE_RUN' in os.environ else ''
                    commit_hash = push_changes(repo, remote_name, badge_branch, badge_name, msg_suffix)
                    if commit_hash is not None:
                        print(f'✅ pushed commit ({commit_hash[:7]}) to remote branch ({badge_branch})')

                        endpoint_badge = create_shieldsio_endpoint_badge(repo, badge_branch, badge_name, badge_url)
                        print(f'\n🎉 Endpoint Badge: {endpoint_badge}')

                    else:
                        print(f'❌ failed to push changes to {remote_name}')

                else:
                    print('✅ found no changes (current is up to date)')

                    endpoint_badge = create_shieldsio_endpoint_badge(repo, badge_branch, badge_name, badge_url)
                    print(f'\n🎉 Endpoint Badge: {endpoint_badge}')

            else:
                print(f'❌ failed to create {badge_name}.json')

    else:
        print('❌ one or more of your inputs failed validations')

    if 'COVERAGE_RUN' in os.environ:
        if cicleanup(repo, remote_name, badge_branch):
            print(f'🗑️ deleted remote branch ({badge_branch})')


if __name__ == '__main__':  # pragma: no cover
    main()
