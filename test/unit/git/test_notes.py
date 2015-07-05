# coding: utf-8
import uuid

from tags.release import Release
from tags import git


def test_basic(repo, release):
    message = uuid.uuid4().hex
    git.release_note(repo, release, message)
    note = repo.show_note(release.ref_name)
    assert note == {'test': {1: message}}


def test_append_same_channel_same_commit(repo):
    first_release = Release(repo, 'test')
    first_release.create_tag()
    first_message = uuid.uuid4().hex
    git.release_note(repo, first_release, first_message)
    assert repo.show_note(first_release.ref_name) == {
        'test': {1: first_message},
    }

    # same channel, release number should be different
    second_release = Release(repo, 'test')
    second_release.create_tag()
    second_message = uuid.uuid4().hex
    git.release_note(repo, second_release, second_message)
    assert repo.show_note(second_release.ref_name) == {
        'test': {
            1: first_message,
            2: second_message,
        }
    }
