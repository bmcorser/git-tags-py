import pytest

import os
import tempfile
import subprocess


@pytest.fixture(scope='session')
def session_repo(request):
    tempdir = tempfile.mkdtemp()
    os.chdir(tempdir)
    subprocess.check_call(['git', 'init'])
    os.mkdir('a')
    os.mknod('a/a')
    subprocess.check_call(['git', 'add', '.'])
    subprocess.check_call(['git', 'commit', '-m', 'Initial commit'])
    subprocess.check_call(['git', 'tag', '-a', 'a', '-m', 'Tag a'])
    os.mkdir('b')
    os.mknod('b/a')
    subprocess.check_call(['git', 'add', '.'])
    subprocess.check_call(['git', 'commit', '-m', 'Second commit'])
    subprocess.check_call(['git', 'tag', '-a', 'b', '-m', 'Tag b'])
    return tempfile
