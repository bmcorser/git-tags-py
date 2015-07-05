# coding: utf-8
# from __future__ import unicode_literals

from click.testing import CliRunner
import pprint
import tags


def test_git_tag_dict(fn_repo):
    'Can parse the return of cat-file into a dictionary'
    commit, time = fn_repo.packages('pkg-a')[0]
    runner = CliRunner()
    cmd = ['release', '-c', 'test', '-m', 'hello', '-r', fn_repo.local]
    result = runner.invoke(tags.cli.command_group, cmd)
    assert result.exit_code == 0
    tag = 'release/test/1'
    repo = tags.git.Repo(fn_repo.local)
    expected = {
        'tag': tag,
        'tagger_name': fn_repo.user_name,
        'tagger_email': fn_repo.user_email,
        'time': str(time),
        'timezone': '+0000',
        'body': {
            'packages': {
                'changed': {
                    'pkg-a': repo.path_tree('pkg-a'),
                },
                'unchanged': {},
            },
        }
    }
    output = repo.tag_dict(tag)
    # pprint.pprint(output)
    # pprint.pprint(expected)
    assert output == expected
