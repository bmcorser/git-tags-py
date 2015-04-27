import subprocess
import click

from . import utils

FMT_NS = 'releases/{release}'
FMT_TAG = FMT_NS.format(release='{pkg}/{commit}')
FMT_TAG_ALIAS = FMT_NS.format(release='{alias}/{pkg}/{commit}')


def fmt_tag(pkg, commit, alias):
    'Return ref name for package, commit and optional alias'
    if alias:
        return FMT_TAG_ALIAS.format(alias=alias, pkg=pkg, commit=commit)
    return FMT_TAG.format(pkg=pkg, commit=commit)


class TagError(Exception):
    'Tell someone a tag exists'
    pass


def has_remote():
    'Test if repo has a remote defined'
    remote_cmd = ['git', 'remote']
    output = subprocess.check_output(remote_cmd)
    return bool(utils.filter_empty_lines(output))


def head_abbrev(directory=None):
    '''
    Return the unambiguous abbreviated sha1 hash of the commit at HEAD,
    optionally for a directory.

    Note: The abbreviated hash can be of variable length.
    '''
    cmd = ['git', 'rev-list', '-1', 'HEAD', '--abbrev-commit']
    if directory:
        cmd.extend(['--', directory])
    return utils.filter_empty_lines(subprocess.check_output(cmd))[0]


def fetch():
    'Fetch tags and commits'
    if not has_remote():
        return
    fetch_cmd = ['git', 'fetch']
    subprocess.check_call(fetch_cmd)
    fetch_tags_cmd = ['git', 'fetch', '--tags']
    subprocess.check_call(fetch_tags_cmd)


def list_tags():
    'List local tags'
    list_tags_cmd = ['git', 'tag', '-l']
    return utils.filter_empty_lines(subprocess.check_output(list_tags_cmd))


def get_tag_list():
    'Fetch tags from remote abd list them'
    fetch()
    return list_tags()


def create_tag(message, name):
    'Create a tag with the passed name and message (default user)'
    cmd = ['git', 'tag', '-a', name, '-m', message]
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if proc.wait() > 0:
        _, stderr = proc.communicate()
        if 'unable to resolve ref' in stderr or 'still refs under' in stderr:
            click.echo('Did you use a package name as an alias?')
            raise TagError(name)
        else:
            raise TagError(name)


def delete_tag(name):
    '''
    Try to delete the named tag, echo stderr if it fails for any other reason
    save for the tag not existing.
    '''
    cmd = ['git', 'tag', '-d', name]
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if proc.wait() > 0:
        _, stderr = proc.communicate()
        if 'not found' in stderr:
            pass
        else:
            click.echo(stderr)


def push_tags():
    'Push local tags to the remote'
    if not has_remote():
        return
    push_tags_cmd = ['git', 'push', '--tags']
    proc = subprocess.Popen(push_tags_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if proc.wait() > 0:
        _, stderr = proc.communicate()
        click.echo("Error pushing release tags: {0}".format(stderr))
        click.echo('This release will not be available until the tags are '
                   'pushed. You may be able to push the tags manually '
                   'with:\n\n'
                   '  git push --tags')


def status():
    'Return True if there are untracked, unstaged or uncommitted files present'
    cmd = ['git', 'status', '--porcelain']
    return subprocess.check_output(cmd)


def tag_refs(namespace):
    'Return the short refs of tags in the passed namespace'
    cmd = [
        'git',
        'for-each-ref',
        '--format',
        '%(refname:short)',
        "refs/tags/{0}".format(namespace),
    ]
    return utils.filter_empty_lines(subprocess.check_output(cmd))


def sort_refs(refs):
    'Return sorted list of passed refs as abbreviated hashes, latest first'
    cmd = ['git', 'rev-list', '--no-walk', '--abbrev-commit']
    map(cmd.append, refs)
    return utils.filter_empty_lines(subprocess.check_output(cmd))


def cat_file(ref):
    'Call cat-file -p on the ref passed'
    cmd = ['git', 'cat-file', '-p', ref]
    return utils.filter_empty_lines(subprocess.check_output(cmd))


def tagger_line_tokens(tokens):
    'Return the tagger name, email, time and timezone for a tagger line'
    for index, token in enumerate(tokens[1:]):
        if '<' in token and '>' in token:
            e_ix = index + 1  # email position
            break
    return (' '.join(tokens[1:e_ix]),) + tuple(tokens[e_ix:])


def tag_dict(tag):
    'Return the contents of a tag as a dictionary'
    contents = cat_file(tag)
    tagger, email, time, timezone = tagger_line_tokens(contents[3].split(' '))
    tag_message = '\n'.join(contents[4:])
    return {
        'tag': tag,
        'tagger_name': tagger,
        'tagger_email': email.strip('<>'),
        'time': time,
        'timezone': timezone,
        'message': tag_message
    }
