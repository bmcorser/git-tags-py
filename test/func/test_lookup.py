# coding: utf-8
from __future__ import unicode_literals
from click.testing import CliRunner
import tags
import yaml
import uuid


def test_cli_lookup_yaml(function_repo):
    'Can lookup the latest release by channel'
    packages = (uuid.uuid4().hex, uuid.uuid4().hex)
    map(function_repo.commit, packages)
    runner = CliRunner()
    map(function_repo.commit, packages)
    print(runner.invoke(tags.cli.command_group, [
        'release',
        '-c', 'test',
        '-m', 'a',
        '-r', function_repo.local,
    ]).output)
    result = runner.invoke(tags.cli.command_group, [
        'lookup', 'test',
        '-r', function_repo.local,
        '-y'
    ])
    changed = yaml.load(result.output)['body']['packages']['changed']
    for package in packages:
        assert package in changed
