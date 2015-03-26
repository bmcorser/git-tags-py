import os
import pytest
from click.testing import CliRunner

import pygit2
import tags


def create_dummy_repo():
    cwd = os.getcwd()
    repo = pygit2.init_repository(cwd)
    os.mkdir('a')
    os.mkdir('b')
    os.mknod('a/a')
    os.mknod('b/a')
    # repo.index.add(cwd)
    author = pygit2.Signature('Alice Author', 'alice@authors.tld')
    committer = pygit2.Signature('Cecil Committer', 'cecil@committers.tld')
    message = 'Inital commit'
    ref = 'refs/heads/master'
    tree = repo.TreeBuilder().write()
    repo.create_commit(ref, author, committer, message, tree, [])
    return repo


@pytest.mark.skipif(True, reason='Not there yet')
def test_cli():
    assert 0
    runner = CliRunner()
    with runner.isolated_filesystem():
        repo = create_dummy_repo()
        result = runner.invoke(tags.cli.main, ['a', 'b'])
        pass
