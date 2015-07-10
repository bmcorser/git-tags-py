'''
Stolen from:
http://stackoverflow.com/questions/6309587/call-up-an-editor-vim-from-a-python-script
'''

import tempfile
import os
from subprocess import call

TEMPLATE = '''\

{0}
# Do not touch the line above.
# Everything below will be removed.

Commits
-------

{1}

Diff
----

{2}
'''


def capture_message(commits, diff):
    'Use the default editor to capture a message'
    editor = os.environ.get('EDITOR', 'vim')
    diff_marker = '# ------------------------ >8 ------------------------'
    tempdir = tempfile.mkdtemp()
    release_diff = os.path.join(tempdir, "release.diff")
    with open(release_diff, 'w') as release_message:
        release_message.write(TEMPLATE.format(
            diff_marker,
            '\n'.join(commits),
            '\n'.join(diff)))
    call([editor, release_diff])
    with open(release_diff, 'r') as release_message:
        content = release_message.readlines()
    lines = content[:content.index(diff_marker)]
    return ''.join(filter(lambda line: not line.startswith('#'), lines))
