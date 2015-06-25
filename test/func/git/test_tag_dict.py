# coding: utf-8
from __future__ import unicode_literals

from click.testing import CliRunner
import tags


def test_git_tag_dict(function_repo):
    'Can parse the return of cat-file into a dictionary'
    commit, time = function_repo.packages('pkg-a')[0]
    runner = CliRunner()
    cmd = ['release', '-m', 'hello']
    runner.invoke(tags.cli.command_group, cmd)
    tag = 'releases/development/1'
    expected = {
        'tag': tag,
        'tagger_name': function_repo.user_name,
        'tagger_email': function_repo.user_email,
        'time': str(time),
        'timezone': '+0000',
        'body': {
            'packages': {
                'changed': {
                    'pkg-a': tags.git.path_tree('pkg-a'),
                },
                'unchanged': {},
            },
        }
    }
    output = tags.git.tag_dict(tag)
    assert output == expected
