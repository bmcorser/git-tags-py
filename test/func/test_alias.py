# coding: utf-8
from __future__ import unicode_literals

import os
from click.testing import CliRunner
import tags


def test_cli_release_alias(function_repo):
    'Releasing packages under an alias is OK'
    function_repo.packages('a', 'b')
    runner = CliRunner()
    release_alias = 'alias'
    result = runner.invoke(tags.cli.command_group, ['release', 'a', 'b', '-a', release_alias, '-m', 'a'])
    assert result.exit_code == os.EX_OK
    assert release_alias in result.output


def test_cli_release_bad_alias(function_repo):
    'Aliasing a release to a package name is not OK'
    function_repo.packages('a', 'b')
    runner = CliRunner()
    print(runner.invoke(tags.cli.command_group, ['release', 'a', 'b', '-m', 'a']).output)  # register packages
    release_alias = 'a'  # same as a package name
    result = runner.invoke(tags.cli.command_group, ['release', 'a', '-a', release_alias, '-m', 'a'])
    assert result.exit_code == os.EX_DATAERR
    assert 'ERROR' in result.output
    assert "'{0}'".format(release_alias) in result.output
