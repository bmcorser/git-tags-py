# coding: utf-8
from __future__ import unicode_literals

import os
from click.testing import CliRunner
import tags


def test_git_tag_dict(function_repo):
    'Can parse the return of cat-file into a dictionary'
    commit, time = function_repo.packages('pkg-a')[0]
    user_message = '''\
My release
----------
Things that happened:
    - This
    - That
    - The other'''
    runner = CliRunner()
    runner.invoke(tags.cli.main, ['release', 'pkg-a', '-a', 'test-alias', '-m', user_message])
    tag = tags.git.tag_refs('releases/test-alias/pkg-a')[0]
    _, _, _, commit = tag.split('/')
    expected = {
        'tag': tag,
        'message': user_message,
        'tagger_name': function_repo.user_name,
        'tagger_email': function_repo.user_email,
        'time': str(time),
        'timezone': '+0000',
    }
    output = tags.git.tag_dict(tag)
    assert output == expected
