import pytest

import functools
import os
import random
import subprocess
import time

from tags import git, utils


def test_get_tag_list(function_repo):
    'Can get a list of tags'
    subprocess.check_call(['git', 'tag', 'a'])
    subprocess.check_call(['git', 'tag', 'b'])
    retval = git.get_tag_list()
    assert retval == ['a', 'b']


def test_create_tag(function_repo):
    'Can create a tag'
    subprocess.check_call(['git', 'tag', 'a'])
    subprocess.check_call(['git', 'tag', 'b'])
    git.create_tag('...', 'c')
    retval = git.get_tag_list()
    assert retval == ['a', 'b', 'c']


def test_create_tag_tagerror(function_repo):
    'The TagError exception is raised in case of error when creating a tag'
    subprocess.check_call(['git', 'tag', 'a/a'])
    with pytest.raises(git.TagError) as exc:
        git.create_tag('...', 'a')
        assert str(exc) == 'a'


def test_delete_tag(function_repo):
    'Can delete a tag'
    subprocess.check_call(['git', 'tag', 'a'])
    subprocess.check_call(['git', 'tag', 'b'])
    git.create_tag('...', 'c')
    assert git.get_tag_list() == ['a', 'b', 'c']
    git.delete_tag('c')
    assert git.get_tag_list() == ['a', 'b']


def test_delete_tag_nonexistant(function_repo):
    'Deleting a nonexistant tag does not cause error state'
    git.delete_tag('z')


def test_push_tags(function_repo):
    'Deleting a nonexistant tag does not cause error state'
    subprocess.check_call(['git', 'tag', 'a'])
    subprocess.check_call(['git', 'tag', 'b'])
    git.create_tag('...', 'c')
    assert git.list_tags() == ['a', 'b', 'c']
    git.push_tags()
    map(git.delete_tag, 'abc')
    assert git.list_tags() == []
    # the function below pulls tags from the remote
    assert git.get_tag_list() == ['a', 'b', 'c']


def test_dirty_clean(function_repo):
    'Dirty returns False when the repo is clean'
    assert bool(git.status()) == False


def test_dirty_untracked(function_repo):
    'Dirty returns True when there are untracked files'
    os.mknod('c')
    assert bool(git.status()) == True


def test_dirty_unstaged(function_repo):
    'Dirty returns True when there are unstaged files'
    os.mknod('c')
    subprocess.check_call(['git', 'add', 'c'])
    subprocess.check_call(['git', 'commit', '-m', 'abxc'])
    with open('c', 'w') as c:
        c.write('abc')
    assert bool(git.status()) == True


def test_dirty_uncommitted(function_repo):
    'Dirty returns True when there are unstaged files'
    os.mknod('c')
    subprocess.check_call(['git', 'add', 'c'])
    assert bool(git.status()) == True


def test_tag_refs(function_repo):
    'Can get tags by namespace'
    x_tags = ('x/x', 'x/y/x', 'x/y/y')
    y_tags = ('y/x', 'y/y', 'y/z')
    tag = functools.partial(git.create_tag, '...')
    map(tag, x_tags)
    map(tag, y_tags)
    assert set(git.tag_refs('x')) == set(x_tags)
    assert set(git.tag_refs('y')) == set(y_tags)


def test_sort_refs(function_repo):
    'Can sort refs'
    cmd = ['git', 'log', 'HEAD', '--format=%h']
    map(function_repo.commit, ('abcxyz'))
    refs = utils.filter_empty_lines(subprocess.check_output(cmd))
    shuffled_refs = random.sample(refs, len(refs))
    assert git.sort_refs(shuffled_refs) == refs


@pytest.mark.parametrize('line,expected', (
    ('tagger Three Part Name <a@b.com> 123 +0',
     ('Three Part Name', '<a@b.com>', '123', '+0')),
    ('tagger Twopart Name <a@b.com> 123 +0',
     ('Twopart Name', '<a@b.com>', '123', '+0')),
    ('tagger Onepartname <a@b.com> 123 +0',
     ('Onepartname', '<a@b.com>', '123', '+0'))))
def test_tagger_line_tokens(line, expected):
    assert git.tagger_line_tokens(line.split(' ')) == expected
