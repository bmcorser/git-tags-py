# coding: utf-8
from __future__ import unicode_literals
from click.testing import CliRunner
import tags
import yaml
import uuid


def test_cli_lookup_yaml(fn_repo):
    'Can lookup the latest release by channel'
    packages = (uuid.uuid4().hex, uuid.uuid4().hex)
    map(fn_repo.commit, packages)
    runner = CliRunner()
    map(fn_repo.commit, packages)
    print(runner.invoke(tags.cli.command_group, [
        'release',
        '-c', 'test',
        '-m', 'a',
        '-r', fn_repo.local,
    ]).output)
    result = runner.invoke(tags.cli.command_group, [
        'lookup', 'test',
        '-r', fn_repo.local,
        '-y'
    ])
    changed = yaml.load(result.output)['body']['packages']['changed']
    for package in packages:
        assert package in changed
