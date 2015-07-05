'''
Stolen from:
http://stackoverflow.com/questions/6309587/call-up-an-editor-vim-from-a-python-script
'''

import tempfile
import os
from subprocess import call


def capture_message(diff):
    'Use the default editor to capture a message'
    editor = os.environ.get('EDITOR', 'vim')
    diff_marker = '# ------------------------ >8 ------------------------\n'
    diff_msg = '''\
# Do not touch the line above.
# Everything below will be removed.

'''
    tempdir = tempfile.mkdtemp()
    release_diff = os.path.join(tempdir, "release.diff")
    with open(release_diff, 'w') as release_message:
        release_message.write('\n\n' + diff_marker + diff_msg + diff)
    call([editor, release_diff])
    with open(release_diff, 'r') as release_message:
        content = release_message.readlines()
    lines = content[:content.index(diff_marker)]
    return ''.join(filter(lambda line: not line.startswith('#'), lines))
