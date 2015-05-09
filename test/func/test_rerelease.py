# coding: utf-8
from __future__ import unicode_literals

import os
from click.testing import CliRunner
import tags


def test_cli_rerelease(function_repo):
    'Rereleasing a package returns proper exit code and message'
    function_repo.packages('a')
    runner = CliRunner()
    runner.invoke(tags.cli.command_group, ['release', 'a', '-m', 'a'])
    result = runner.invoke(tags.cli.command_group, ['release', 'a', '-m', 'a'])
    assert result.exit_code == os.EX_USAGE
    assert 'package hasn’t changed' in result.output


def test_cli_rerelease_alias(function_repo):
    'Releasing a package under an alias is OK'
    function_repo.packages('a')
    runner = CliRunner()
    runner.invoke(tags.cli.command_group, ['release', 'a', '-m', 'a'])
    release_alias = 'alias'
    result = runner.invoke(tags.cli.command_group, ['release', 'a', '-a', release_alias, '-m', 'a'])
    assert result.exit_code == os.EX_OK
    assert release_alias in result.output


def test_cli_rerelease_same_alias(function_repo):
    'Rereleasing under the same alias is not OK'
    function_repo.packages('a')
    runner = CliRunner()
    runner.invoke(tags.cli.command_group, ['release', 'a', '-m', 'a']).output
    release_alias = 'release-alias'
    runner.invoke(tags.cli.command_group, ['release', 'a', '-a', release_alias, '-m', 'a']).output
    result = runner.invoke(tags.cli.command_group, ['release', 'a', '-a', release_alias, '-m', 'a'])
    assert result.exit_code == os.EX_USAGE
    assert 'package hasn’t changed' in result.output


def test_cli_rerelease_alias_pkg(function_repo):
    'Adding a package to an alias is fine'
    function_repo.packages('a', 'b')
    runner = CliRunner()
    runner.invoke(tags.cli.command_group, ['release', 'a', '-m', 'a']).output
    release_alias = 'release-alias'
    runner.invoke(tags.cli.command_group, ['release', 'a', '-a', release_alias, '-m', 'a']).output
    result = runner.invoke(tags.cli.command_group, ['release', 'b', '-a', release_alias, '-m', 'a'])
    assert result.exit_code == os.EX_OK
    assert release_alias in result.output
