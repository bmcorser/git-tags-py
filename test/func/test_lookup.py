# coding: utf-8
from __future__ import unicode_literals
from click.testing import CliRunner
import tags
import os
import subprocess


def test_cli_lookup_yaml(function_repo):
    'Can lookup the latest a package release by name'
    map(function_repo.commit, ('a', 'b'))
    runner = CliRunner()
    # update package 'a'
    function_repo.commit('a')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()[:7]
    # release package 'b'
    print(runner.invoke(tags.cli.command_group, ['release','b', '-m', 'a']).output)
    result = runner.invoke(tags.cli.command_group, ['lookup', 'b', '--yaml'])
    assert commit in result.output
