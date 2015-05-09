# coding: utf-8
from __future__ import unicode_literals

import os
from click.testing import CliRunner
import tags


def test_cli_rerelease(function_repo):
    'Rereleasing a package returns proper exit code and message'
    function_repo.packages('a', 'b', 'c')
    runner = CliRunner()
    runner.invoke(tags.cli.command_group, ['release', 'a', '-m', 'a'])
    result = runner.invoke(tags.cli.command_group, ['release', 'a', '-m', 'a'])
    assert result.exit_code == os.EX_USAGE
    assert 'package hasn’t changed' in result.output
