# coding: utf-8
from __future__ import unicode_literals

from click.testing import CliRunner
from tags.cli import command_group as tags_cli
from tags import git


def test_cli_lazy_release_a_only(function_repo):
    'Releasing with * does not release things that do not need to be released'
    function_repo.packages('a', 'b', 'c')
    runner = CliRunner()
    runner.invoke(tags_cli, ['release', 'a', 'b', 'c', '-m', 'a'])
    commit, _ = function_repo.commit('a')
    bad_tag_b = git.fmt_tag('b', commit, None)
    bad_tag_c = git.fmt_tag('c', commit, None)
    result = runner.invoke(tags_cli, ['release', '*', '-m', 'a'])
    assert bad_tag_b not in result.output
    assert bad_tag_c not in result.output


def test_cli_lazy_release_a_b_c(function_repo):
    'Rereleasing a package returns proper exit code and message'
    function_repo.packages('a', 'b', 'c')
    runner = CliRunner()
    result = runner.invoke(tags_cli, ['release', '*', '-m', 'a'])
    assert 'a b c' in result.output
