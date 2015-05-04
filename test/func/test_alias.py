# coding: utf-8
from __future__ import unicode_literals

import os
from click.testing import CliRunner
import tags


def test_cli_release_alias(monkeypatch, function_repo):
    'Releasing packages under an alias is OK'
    function_repo.packages('a', 'b')
    monkeypatch.setattr(tags.notes, 'capture_message', lambda: 'User message')
    runner = CliRunner()
    release_alias = 'alias'
    result = runner.invoke(tags.cli.main, ['release', 'a', 'b', '-a', release_alias])
    assert result.exit_code == os.EX_OK
    assert release_alias in result.output


def test_cli_release_bad_alias(monkeypatch, function_repo):
    'Aliasing a release to a package name is not OK'
    function_repo.packages('a', 'b')
    monkeypatch.setattr(tags.notes, 'capture_message', lambda: 'User message')
    runner = CliRunner()
    print(runner.invoke(tags.cli.main, ['release', 'a', 'b']).output)  # register packages
    release_alias = 'a'  # same as a package name
    result = runner.invoke(tags.cli.main, ['release', 'a', '-a', release_alias])
    assert result.exit_code == os.EX_DATAERR
    assert 'ERROR' in result.output
    assert "'{0}'".format(release_alias) in result.output
