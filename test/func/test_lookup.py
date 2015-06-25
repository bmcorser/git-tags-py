# coding: utf-8
from __future__ import unicode_literals
from click.testing import CliRunner
import tags
import yaml
import uuid


def test_cli_lookup_yaml(function_repo):
    'Can lookup the latest a package release by name'
    packages = (uuid.uuid4().hex, uuid.uuid4().hex)
    map(function_repo.commit, packages)
    runner = CliRunner()
    map(function_repo.commit, packages)
    print(runner.invoke(tags.cli.command_group, ['release', '-m', 'a']).output)
    result = runner.invoke(tags.cli.command_group, ['lookup', 'development'])
    changed = yaml.load(result.output)['body']['packages']['changed']
    for package in packages:
        assert package in changed
