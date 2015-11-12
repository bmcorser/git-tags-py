import tempfile
import os
from subprocess import call

TEMPLATE = '''\

{0}\
# Do not touch the line above.
# Everything below will be removed.

Commits
-------

{1}

Diff
----

{2}

{3}
'''


def capture_message(commits, diff_stat, diff_patch):
    'Use the default editor to capture a message'
    editor = os.environ.get('EDITOR', 'vim')
    diff_marker = '# ------------------------ >8 ------------------------\n'
    tempdir = tempfile.mkdtemp()
    release_diff = os.path.join(tempdir, "release.diff")
    with open(release_diff, 'w') as release_message:
        release_message.write(TEMPLATE.format(
            diff_marker, '\n'.join(commits), diff_stat, diff_patch
        ))
    call([editor, release_diff])
    with open(release_diff, 'r') as release_message:
        content = release_message.readlines()
    try:
        lines = content[:content.index(diff_marker)]
    except ValueError as exc:
        if diff_marker.strip() in exc.message:
            lines = content
    return ''.join(filter(lambda line: not line.startswith('#'), lines))
