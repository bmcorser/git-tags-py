import pytest
from tags import git


def test_get_tag_list(session_repo):
    retval = git.get_tag_list()
    assert retval == ['a', 'b']

def test_cli_tag_exists(session_repo):
    git.create_tag('abc', 'message')
    with pytest.raises(git.TagExists):
        git.create_tag('abc', 'message')
