# coding: utf-8
from __future__ import unicode_literals

import pytest

import datetime
import os
from click.testing import CliRunner
import tags


@pytest.mark.skipif(True, reason='It takes a while')
def test_cli_rerelease(nasty_repo):
    'Releasing takes how long with 1000'
    nasty_repo.releases(1000)
    runner = CliRunner()
    start = datetime.datetime.now()
    result = runner.invoke(tags.cli.main, ['release', 'a', '-m', '...'])
    delta = datetime.datetime.now() - start
    print(delta)
    import ipdb;ipdb.set_trace()
    assert 0
    # assert result.exit_code == os.EX_USAGE
