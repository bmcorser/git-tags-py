# coding: utf-8
from __future__ import unicode_literals

import os
from click.testing import CliRunner
import tags


def test_cli_rerelease(monkeypatch, function_repo):
    'Rereleasing a package returns proper exit code and message'
    function_repo.packages('a', 'b', 'c')
    monkeypatch.setattr(tags.notes, 'capture_message', lambda: 'User message')
    runner = CliRunner()
    runner.invoke(tags.cli.main, ['release', 'a'])
    result = runner.invoke(tags.cli.main, ['release', 'a'])
    assert result.exit_code == os.EX_USAGE
    assert 'package hasn’t changed' in result.output
