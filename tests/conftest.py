#!/usr/bin/env python

import os

import git
import pytest


@pytest.fixture
def get_repo():
    """
    Get repo class object 'git.repo.base.Repo'

    Return: repo object
    """
    return git.Repo(os.getcwd())
