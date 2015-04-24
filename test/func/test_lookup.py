# coding: utf-8
from __future__ import unicode_literals
from click.testing import CliRunner
import tags
import os
import subprocess


def test_cli_lookup(monkeypatch, function_repo):
    'Can lookup the latest a package release by name'
    monkeypatch.setattr(tags.message, 'capture_message', lambda: 'User message')
    map(function_repo.commit, ('a', 'b'))
    runner = CliRunner()
    # update package 'a'
    function_repo.commit('a')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()[:7]
    # release package 'b'
    print(runner.invoke(tags.cli.main, ['release','b']).output)
    result = runner.invoke(tags.cli.main, ['lookup', 'b'])
    assert commit in result.output
