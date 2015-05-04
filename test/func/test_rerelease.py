# coding: utf-8
from __future__ import unicode_literals

import os
from click.testing import CliRunner
import tags


def test_cli_rerelease(monkeypatch, function_repo):
    'Rereleasing a package returns proper exit code and message'
    function_repo.packages('a')
    monkeypatch.setattr(tags.notes, 'capture_message', lambda: 'User message')
    runner = CliRunner()
    runner.invoke(tags.cli.main, ['release', 'a'])
    result = runner.invoke(tags.cli.main, ['release', 'a'])
    assert result.exit_code == os.EX_USAGE
    assert 'package hasn’t changed' in result.output


def test_cli_rerelease_alias(monkeypatch, function_repo):
    'Releasing a package under an alias is OK'
    function_repo.packages('a')
    monkeypatch.setattr(tags.notes, 'capture_message', lambda: 'User message')
    runner = CliRunner()
    runner.invoke(tags.cli.main, ['release', 'a'])
    release_alias = 'alias'
    result = runner.invoke(tags.cli.main, ['release', 'a', '-a', release_alias])
    assert result.exit_code == os.EX_OK
    assert release_alias in result.output


def test_cli_rerelease_same_alias(monkeypatch, function_repo):
    'Rereleasing under the same alias is not OK'
    function_repo.packages('a')
    monkeypatch.setattr(tags.notes, 'capture_message', lambda: 'User message')
    runner = CliRunner()
    runner.invoke(tags.cli.main, ['release', 'a']).output
    release_alias = 'release-alias'
    runner.invoke(tags.cli.main, ['release', 'a', '-a', release_alias]).output
    result = runner.invoke(tags.cli.main, ['release', 'a', '-a', release_alias])
    assert result.exit_code == os.EX_USAGE
    assert 'package hasn’t changed' in result.output


def test_cli_rerelease_alias_pkg(monkeypatch, function_repo):
    'Adding a package to an alias is fine'
    function_repo.packages('a', 'b')
    monkeypatch.setattr(tags.notes, 'capture_message', lambda: 'User message')
    runner = CliRunner()
    runner.invoke(tags.cli.main, ['release', 'a']).output
    release_alias = 'release-alias'
    runner.invoke(tags.cli.main, ['release', 'a', '-a', release_alias]).output
    result = runner.invoke(tags.cli.main, ['release', 'b', '-a', release_alias])
    assert result.exit_code == os.EX_OK
    assert release_alias in result.output
