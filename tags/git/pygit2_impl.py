import re
import pygit2

_REPO = None

def get_repo():
    global _REPO
    if not _REPO:
        _REPO = pygit2.Repository('.')
    return _REPO


def get_head_sha1():
    'Return the sha1 hash of the commit at HEAD'
    repo = get_repo()
    return repo.revparse_single('HEAD').hex


def get_tag_list():
    'Return all the tags in the repo'
    repo = get_repo()
    regex = re.compile('^refs/tags')
    is_tag = lambda r: regex.match(r)
    strip_prefix = lambda t: t.replace('refs/tags/', '')
    return list(map(strip_prefix, filter(is_tag, repo.listall_references())))


def create_tag(name, message):
    'Create a tag with the passed name and message (default user)'
    repo = get_repo()
    default_user = pygit2.Signature(repo.config['user.name'],
                                    repo.config['user.email'])
    repo.create_tag(name, get_head_sha1(), pygit2.GIT_OBJ_COMMIT,
                    default_user, message)


if __name__ == '__main__':
    get_tag_list()
