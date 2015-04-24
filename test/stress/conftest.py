import pytest

import collections
import functools
import os
import tempfile
import shutil
import subprocess

from tags import git as tags_git


def create_temp_repo():
    repo_dir = tempfile.mkdtemp()
    os.chdir(repo_dir)
    os.mkdir('remote_repo')
    os.chdir('remote_repo')
    subprocess.check_call(['git', 'init'])
    global time
    time = 1329828782
    def new_time():
        global time
        time += 100
        os.environ['GIT_COMMITTER_DATE'] = "{0} +0000".format(time)
        os.environ['GIT_AUTHOR_DATE'] = "{0} +0000".format(time)
    def touch(name):
        path = os.path.join(name, 'deploy')
        try:
            os.mkdir(name)
            os.mknod(path)
        except OSError as exc:
            if exc.errno != 17:
                raise
        new_time()
        with open(path, 'w') as deploy_file:
            deploy_file.write(str(time))
    def add(name='.'):
        subprocess.check_call(['git', 'add', name])
    def _commit(name='...'):
        subprocess.check_call(['git', 'commit', '-m', name])
        return tags_git.head_abbrev()
    def commit(name):
        'Touch the deploy file in the named package and commit it'
        touch(name)
        add(name)
        return _commit(name)
    def packages(*names):
        for name in names:
            commit(name)
    os.mknod('init')
    subprocess.check_call(['git', 'add', '.'])
    new_time()
    subprocess.check_call(['git', 'commit', '-m', 'Initial commit'])
    '''subprocess.check_call(['git', 'tag', '-a', 'a', '-m', 'Tag a'])'''
    os.chdir(repo_dir)
    subprocess.check_call(['git', 'clone', 'remote_repo', 'local_repo'])
    os.chdir('local_repo')
    repo_dict = {
        'commit': commit,
        'packages': packages,
        'touch': touch,
        'add': add,
        'raw_commit': _commit,
        'dir': repo_dir,
    }
    return collections.namedtuple('repo', repo_dict.keys())(**repo_dict)


@pytest.yield_fixture(scope='session')
def nasty_repo():
    repo = create_temp_repo()
    pkgs = 'abcde'
    def releases(count):
        for x in range(count):
            for pkg in pkgs:
                repo.touch(pkg)
            repo.add()
            commit = repo.raw_commit()
            tag = functools.partial(tags_git.create_tag, '...')
            for pkg in pkgs:
                tag(tags_git.FMT_TAG.format(pkg=pkg, commit=commit[:7]))
    nasty_dict = {
        'repo': repo,
        'releases': releases,
    }
    yield collections.namedtuple('nasty', nasty_dict.keys())(**nasty_dict)
    shutil.rmtree(repo.dir)
