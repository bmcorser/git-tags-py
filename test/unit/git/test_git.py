import pytest
from tags import git


def test_get_tag_list(function_repo):
    'Can get a list of tags'
    retval = git.get_tag_list()
    assert retval == ['a', 'b']


def test_create_tag(function_repo):
    'Can create a tag'
    git.create_tag('...', 'c')
    retval = git.get_tag_list()
    assert retval == ['a', 'b', 'c']


def test_create_tag_tagerror(function_repo):
    'The TagError exception is raised in case of error when creating a tag'
    with pytest.raises(git.TagError) as exc:
        git.create_tag('...', 'a')
        assert str(exc) == 'a'


def test_delete_tag(function_repo):
    'Can delete a tag'
    git.create_tag('...', 'c')
    assert git.get_tag_list() == ['a', 'b', 'c']
    git.delete_tag('c')
    assert git.get_tag_list() == ['a', 'b']


def test_delete_tag_nonexistant(function_repo):
    'Deleting a nonexistant tag does not cause error state'
    git.delete_tag('z')


def test_push_tags(function_repo):
    'Deleting a nonexistant tag does not cause error state'
    git.create_tag('...', 'c')
    assert git.list_tags() == ['a', 'b', 'c']
    git.push_tags()
    map(git.delete_tag, 'abc')
    assert git.list_tags() == []
    # the function below pulls tags from the remote
    assert git.get_tag_list() == ['a', 'b', 'c']
