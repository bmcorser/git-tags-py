import pytest

import functools
import os
import random
import subprocess
import time

from tags import git, utils

TAGS_GLOB = 'refs/tags/*'

def test_create_tag(fn_repo):
    'Can create a tag'
    fn_repo.repo.run(['tag', 'a'])
    fn_repo.repo.run(['tag', 'b'])
    fn_repo.repo.create_tag('...', 'c')
    retval = git.refs_glob(TAGS_GLOB)
    assert retval == ['a', 'b', 'c']


def test_create_tag_tagerror(fn_repo):
    'The TagError exception is raised in case of error when creating a tag'
    subprocess.check_call(['git', 'tag', 'a/a'])
    with pytest.raises(git.TagError) as exc:
        git.create_tag('...', 'a')
        assert str(exc) == 'a'


def test_delete_tag(fn_repo):
    'Can delete a tag'
    subprocess.check_call(['git', 'tag', 'a'])
    subprocess.check_call(['git', 'tag', 'b'])
    git.create_tag('...', 'c')
    assert git.refs_glob(TAGS_GLOB) == ['a', 'b', 'c']
    git.delete_tag('c')
    assert subprocess.check_output(['git', 'tag']) == 'a\nb\n'


def test_delete_tag_nonexistant(fn_repo):
    'Deleting a nonexistant tag does not cause error state'
    git.delete_tag('z')


def test_push_tags(fn_repo):
    'Deleting a nonexistant tag does not cause error state'
    subprocess.check_call(['git', 'tag', 'a'])
    subprocess.check_call(['git', 'tag', 'b'])
    git.create_tag('...', 'c')
    assert git.refs_glob(TAGS_GLOB) == ['a', 'b', 'c']
    git.push_tags()
    map(git.delete_tag, 'abc')
    assert subprocess.check_output(['git', 'tag']) == ''
    # the function below pulls tags from the remote
    assert git.refs_glob(TAGS_GLOB) == ['a', 'b', 'c']


def test_dirty_clean(fn_repo):
    'Dirty returns False when the repo is clean'
    assert bool(git.status()) == False


def test_dirty_untracked(fn_repo):
    'Dirty returns True when there are untracked files'
    fn_repo.touch('c')
    assert bool(git.status()) == True


def test_dirty_unstaged(fn_repo):
    'Dirty returns True when there are unstaged files'
    fn_repo.touch('c')
    subprocess.check_call(['git', 'add', 'c'])
    subprocess.check_call(['git', 'commit', '-m', 'abxc'])
    with open('c', 'w') as c:
        c.write('abc')
    assert bool(git.status()) == True


def test_dirty_uncommitted(fn_repo):
    'Dirty returns True when there are unstaged files'
    fn_repo.touch('c')
    subprocess.check_call(['git', 'add', 'c'])
    assert bool(git.status()) == True


def test_tag_refs(fn_repo):
    'Can get tags by namespace'
    x_tags = ('x/x', 'x/y/x', 'x/y/y')
    y_tags = ('y/x', 'y/y', 'y/z')
    tag = functools.partial(git.create_tag, '...')
    map(tag, x_tags)
    map(tag, y_tags)
    assert set(git.refs_glob('refs/tags/x/**')) == set(x_tags)
    assert set(git.refs_glob('refs/tags/y/**')) == set(y_tags)


@pytest.mark.parametrize('line,expected', (
    ('tagger Three Part Name <a@b.com> 123 +0',
     ('Three Part Name', '<a@b.com>', '123', '+0')),
    ('tagger Twopart Name <a@b.com> 123 +0',
     ('Twopart Name', '<a@b.com>', '123', '+0')),
    ('tagger Onepartname <a@b.com> 123 +0',
     ('Onepartname', '<a@b.com>', '123', '+0'))))
def test_tagger_line_tokens(line, expected):
    assert git.tagger_line_tokens(line.split(' ')) == expected
