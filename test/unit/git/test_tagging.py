import pytest

import functools

from tags import git

TAGS_GLOB = 'refs/tags/*'


def test_create_tag(repo):
    'Can create a tag'
    repo.run(['tag', 'a'])
    repo.run(['tag', 'b'])
    repo.create_tag('...', 'c')
    retval = repo.refs_glob(TAGS_GLOB)
    assert retval == ['a', 'b', 'c']


def test_create_tag_tagerror(repo):
    'The TagError exception is raised in case of error when creating a tag'
    repo.run(['tag', 'a/a'])
    with pytest.raises(git.TagError) as exc:
        repo.create_tag('...', 'a')
        assert str(exc) == 'a'


def test_delete_tag(repo):
    'Can delete a tag'
    repo.run(['tag', 'a'])
    repo.run(['tag', 'b'])
    repo.create_tag('...', 'c')
    assert repo.refs_glob(TAGS_GLOB) == ['a', 'b', 'c']
    repo.delete_tag('c')
    _, (out, _) = repo.run(['tag'])
    assert out == ['a', 'b']


def test_delete_tag_nonexistant(repo):
    'Deleting a nonexistant tag does not cause error state'
    repo.delete_tag('z')


def test_push_tags(repo):
    'Deleting a nonexistant tag does not cause error state'
    repo.run(['tag', 'a'])
    repo.run(['tag', 'b'])
    repo.create_tag('...', 'c')
    assert repo.refs_glob(TAGS_GLOB) == ['a', 'b', 'c']
    repo.push_ref(TAGS_GLOB)
    map(repo.delete_tag, 'abc')
    _, (out, _) = repo.run(['tag'])
    assert out == []
    # the function below pulls tags from the remote
    assert repo.refs_glob(TAGS_GLOB) == ['a', 'b', 'c']


def test_tag_refs(repo):
    'Can get tags by namespace'
    x_tags = ('x/x', 'x/y/x', 'x/y/y')
    y_tags = ('y/x', 'y/y', 'y/z')
    tag = functools.partial(repo.create_tag, '...')
    map(tag, x_tags)
    map(tag, y_tags)
    assert set(repo.refs_glob('refs/tags/x/**')) == set(x_tags)
    assert set(repo.refs_glob('refs/tags/y/**')) == set(y_tags)


@pytest.mark.parametrize('line,expected', (
    ('tagger Three Part Name <a@b.com> 123 +0',
     ('Three Part Name', '<a@b.com>', '123', '+0')),
    ('tagger Twopart Name <a@b.com> 123 +0',
     ('Twopart Name', '<a@b.com>', '123', '+0')),
    ('tagger Onepartname <a@b.com> 123 +0',
     ('Onepartname', '<a@b.com>', '123', '+0'))))
def test_tagger_line_tokens(line, expected):
    assert git.tagger_line_tokens(line.split(' ')) == expected
