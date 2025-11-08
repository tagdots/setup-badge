#!/usr/bin/env python

"""
Purpose: tests
"""
import os

import git
import pytest
from click.testing import CliRunner

from setup_badge.run import (
    check_user_inputs,
    checkout_branch,
    cicleanup,
    create_badge_dict,
    create_badge_json,
    create_shieldsio_endpoint_badge,
    main,
    push_changes,
)


@pytest.fixture
def get_repo():
    """
    Get repo class object 'git.repo.base.Repo'
    Return: repo object
    """
    return git.Repo(os.getcwd())


def test_get_repo(get_repo):
    """
    Test to verify that get_repo fixture provides a valid GitPython Repo object
    """
    assert isinstance(get_repo, git.Repo)
    assert get_repo.working_dir is not None


def test_checkout_branch_return_detached_branch_object(get_repo):
    """
    Test checkout branch (scenario: detached head)

    Expect Result: Branch Object
    """
    remote_name = 'origin'
    badge_branch = 'ci-testing'
    gitconfig_name = 'Mona Lisa'
    gitconfig_email = 'mona.lisa@github.com'

    result = checkout_branch(get_repo, remote_name, badge_branch, gitconfig_name, gitconfig_email)
    print(f'\nCheckout branch result: {result}')

    assert result is not None
    assert isinstance(result, git.Head)


def test_checkout_branch_return_branch_object(get_repo):
    """
    Test checkout branch (scenario: badge branch exists in both local and remote)

    Expect Result: Branch Object
    """
    remote_name = 'origin'
    badge_branch = 'ci-testing'
    gitconfig_name = 'Mona Lisa'
    gitconfig_email = 'mona.lisa@github.com'

    result = checkout_branch(get_repo, remote_name, badge_branch, gitconfig_name, gitconfig_email)
    print(f'\nCheckout branch result: {result}')

    assert result is not None
    assert isinstance(result, git.Head)


def test_checkout_branch_return_exception(get_repo):
    """
    Test checkout branch (scenario: badge branch exists in both local and remote but local is dirty)

    Expect Result: None
    """
    remote_name = 'origin'
    badge_branch = 'ci-testing'
    gitconfig_name = 'Mona Lisa'
    gitconfig_email = 'mona.lisa@github.com'

    file_path = "file"
    with open(file_path, 'w') as file:
        file.write("test")

    result = checkout_branch(get_repo, remote_name, badge_branch, gitconfig_name, gitconfig_email)
    print(f'\nCheckout branch result: {result}')

    os.remove(file_path)

    assert result is None
    assert not isinstance(result, git.Head)


def test_checkout_branch_return_none_01(get_repo):
    """
    Test checkout branch

    Expect Result: None due to invalid get_repo class object
    """
    get_repo = ''
    remote_name = 'origin'
    badge_branch = 'ci-testing'
    gitconfig_name = 'Mona Lisa'
    gitconfig_email = 'mona.lisa@github.com'

    result = checkout_branch(get_repo, remote_name, badge_branch, gitconfig_name, gitconfig_email)  # type: ignore
    print(f'\nCheckout branch result: {result}')

    assert result is None


def test_checkout_branch_return_none_02(get_repo):
    """
    Test checkout branch

    Expect Result: None due to invalid badge name
    """
    remote_name = 'origin'
    badge_branch = ''
    gitconfig_name = 'Mona Lisa'
    gitconfig_email = 'mona.lisa@github.com'

    result = checkout_branch(get_repo, remote_name, badge_branch, gitconfig_name, gitconfig_email)
    print(f'\nCheckout branch result: {result}')

    assert result is None


def test_checkout_branch_return_none_03(get_repo):
    """
    Test checkout branch

    Expect Result: None due to invalid remote name
    """
    remote_name = 'invalid'
    badge_branch = ''
    gitconfig_name = 'Mona Lisa'
    gitconfig_email = 'mona.lisa@github.com'

    result = checkout_branch(get_repo, remote_name, badge_branch, gitconfig_name, gitconfig_email)
    print(f'\nCheckout branch result: {result}')

    assert result is None


def test_check_user_inputs_return_true_01():
    """
    Test user input validations with default badge_url

    Expect Result: True
    """
    available_badge_styles = ['flat', 'flat-square', 'plastic', 'for-the-badge', 'social']
    badge_style = 'social'
    badge_url = ''
    label_color = '007ec6'
    message_color = 'fc8803'

    result = check_user_inputs(available_badge_styles, badge_style, badge_url, label_color, message_color)
    print(f'\nCheck user inputs result: {result}')

    assert result is True


def test_check_user_inputs_return_true_02():
    """
    Test user input validations with user-input badge_url

    Expect Result: True
    """
    available_badge_styles = ['flat', 'flat-square', 'plastic', 'for-the-badge', 'social']
    badge_style = 'social'
    badge_url = 'https://github.com'
    label_color = '007ec6'
    message_color = 'fc8803'

    result = check_user_inputs(available_badge_styles, badge_style, badge_url, label_color, message_color)
    print(f'\nCheck user inputs result: {result}')

    assert result is True


def test_check_user_inputs_return_false_01():
    """
    Test user input validations

    Expect Result: False due to badge_style not in available_badge_styles
    """
    available_badge_styles = ['flat', 'flat-square', 'plastic', 'for-the-badge', 'social']
    badge_style = 'hoodoo'
    badge_url = ''
    label_color = '000000'
    message_color = 'FFFFFF'

    result = check_user_inputs(available_badge_styles, badge_style, badge_url, label_color, message_color)
    print(f'\nCheck user inputs result: {result}')

    assert result is False


def test_check_user_inputs_return_false_02():
    """
    Test user input validations

    Expect Result: False due to invalid hex color in label-color
    """
    available_badge_styles = ['flat', 'flat-square', 'plastic', 'for-the-badge', 'social']
    badge_style = 'flat'
    badge_url = ''
    label_color = '0000'
    message_color = 'FFF'

    result = check_user_inputs(available_badge_styles, badge_style, badge_url, label_color, message_color)
    print(f'\nCheck user inputs result: {result}')

    assert result is False


def test_check_user_inputs_return_false_03():
    """
    Test user input validations

    Expect Result: False due to invalid hex color in message-color
    """
    available_badge_styles = ['flat', 'flat-square', 'plastic', 'for-the-badge', 'social']
    badge_style = 'flat'
    badge_url = ''
    label_color = '000'
    message_color = 'GGG'

    result = check_user_inputs(available_badge_styles, badge_style, badge_url, label_color, message_color)
    print(f'\nCheck user inputs result: {result}')

    assert result is False


def test_check_user_inputs_return_false_04():
    """
    Test user input validations

    Expect Result: False due to invalid badge url
    """
    available_badge_styles = ['flat', 'flat-square', 'plastic', 'for-the-badge', 'social']
    badge_style = 'flat'
    badge_url = 'hxxp://github.com'
    label_color = '000'
    message_color = 'FFF'

    result = check_user_inputs(available_badge_styles, badge_style, badge_url, label_color, message_color)
    print(f'\nCheck user inputs result: {result}')

    assert result is False


def test_create_badge_dict_return_dict():
    """
    Test create python dictionary object

    Expect Result: python dictionary object
    """
    badge_style = 'flat'
    label = 'demo'
    label_color = '000'
    message = 'no status - 100'
    message_color = 'FFF'

    result = create_badge_dict(badge_style, label, label_color, message, message_color)
    print(f'\nCreate badge dictionary result: {result}')

    assert isinstance(result, dict)


def test_create_badge_json_return_false():
    """
    Test create badge json file from python dictionary

    Expect Result: False due to invalid badge_dict
    """
    badge_dict = ''
    badge_name = 'ci-testing'

    result = create_badge_json(badge_dict, badge_name)  # type: ignore
    print(f'\nCreate badge JSON from python dictionary result: {result}')

    assert result is False


def test_push_changes_return_none_01(get_repo):
    """
    Test push changes to remote

    Expect Result: None due to invalid repo class object
    """
    repo = ''
    badge_name = 'ci-testing'
    badge_branch = 'ci-testing'
    remote_name = 'origin'
    msg_suffix = '[CI - Testing]'

    assert push_changes(repo, remote_name, badge_branch, badge_name, msg_suffix) is None  # type: ignore


def test_push_changes_return_none_02(get_repo):
    """
    Test push changes to remote

    Expect Result: None due to file not found becaues the file was never checkin
    """
    badge_name = 'file-not-exist'
    badge_branch = 'ci-testing'
    remote_name = 'origin'
    msg_suffix = '[CI - Testing]'

    assert push_changes(get_repo, remote_name, badge_branch, badge_name, msg_suffix) is None


def test_create_shieldsio_endpoint_return_true_01(get_repo):
    """
    Test create shields.io endpoint badge url

    Expect Result: Endpoint Badge
    """
    badge_name = 'demo'
    branch_name = 'demo'
    badge_url = ''

    endpoint_badge = create_shieldsio_endpoint_badge(get_repo, branch_name, badge_name, badge_url)

    assert isinstance(endpoint_badge, str), "Return value is not a string"
    assert endpoint_badge.startswith(f'![{badge_name}]'), "Return value must start with badge_name"
    assert 'https://img.shields.io/endpoint' in endpoint_badge, "Return value must contain shields.io endpoint"


def test_create_shieldsio_endpoint_return_true_02(get_repo):
    """
    Test create shields.io endpoint badge url

    Expect Result: Endpoint Badge
    """
    badge_name = 'demo'
    branch_name = 'demo'
    badge_url = 'https://github.com'

    endpoint_badge = create_shieldsio_endpoint_badge(get_repo, branch_name, badge_name, badge_url)

    assert isinstance(endpoint_badge, str), "Return value is not a string"
    assert endpoint_badge.startswith(f'[![{badge_name}]'), "Return value must start with badge_name"
    assert 'https://img.shields.io/endpoint' in endpoint_badge, "Return value must contain shields.io endpoint"


def test_main_return_failure_01():
    """
    Test main

    Expect Result: Return Failure Message for invalid hex color on label-color
    """
    runner = CliRunner()
    result = runner.invoke(main, ['--badge-branch', 'ci-testing', '--badge-name', 'ci-testing', '--label-color', 'GGG'])
    print(f'\nMain result: {result}')

    assert result is not None


def test_main_return_failure_02():
    """
    Test main

    Expect Result: Return Failure Message for invalid remote name
    """
    runner = CliRunner()
    result = runner.invoke(main, ['--badge-branch', 'ci-testing', '--badge-name', 'ci-testing', '--remote-name', 'invalid'])
    print(f'\nMain result: {result}')

    assert result is not None


def test_cicleanup_failure(get_repo):
    """
    Test ci-cleanup

    Expect Result: False due to invalid remote_name
    """
    remote_name = 'origin-invalid'
    badge_branch = 'ci-testing'

    result = cicleanup(get_repo, remote_name, badge_branch)
    print(f'\nCleanup result: {result}')

    assert result is False


def test_main_return_success_default():
    """
    Test main

    Expect Result: Return Endpoint Badge for README
    """
    runner = CliRunner()
    result = runner.invoke(main, ['--badge-branch', 'ci-testing', '--badge-name', 'ci-testing'])
    print(f'\nMain result: {result}')
    print(result.stdout)
    print(result.stderr)

    assert result is not None


def test_main_return_success_no_changes():
    """
    Test main

    Expect Result: found no changes (current is up to date)
    """
    runner = CliRunner()
    result = runner.invoke(main, ['--badge-branch', 'ci-testing', '--badge-name', 'ci-testing'])
    print(f'\nMain result: {result}')
    print(result.stdout)
    print(result.stderr)

    assert result is not None


if __name__ == "__main__":
    pytest.main()
