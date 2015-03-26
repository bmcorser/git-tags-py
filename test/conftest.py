import pytest

import os
import tempfile
import subprocess


def create_repo():
    tempdir = tempfile.mkdtemp()
    os.chdir(tempdir)
    subprocess.check_call(['git', 'init'])
    os.mkdir('a')
    os.mkdir('b')
    os.mknod('a/a')
    os.mknod('b/a')
    subprocess.check_call(['git', 'add', 'a', 'b'])
    subprocess.check_call(['git', 'commit', '-m', 'Initial commit'])
    return tempdir


@pytest.fixture(scope='session')
def session_repo(request):
    return create_repo()


@pytest.fixture
def function_repo(request):
    return create_repo()
