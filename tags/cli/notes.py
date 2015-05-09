'''
Stolen from:
http://stackoverflow.com/questions/6309587/call-up-an-editor-vim-from-a-python-script
'''

import tempfile
import os
from subprocess import call


def capture_message():
    'Use the default editor to capture a message'
    editor = os.environ.get('EDITOR', 'vim')
    initial_message = ''
    with tempfile.NamedTemporaryFile(suffix=".tmp") as message_file:
        message_file.file.write(initial_message)
        message_file.file.flush()
        call([editor, message_file.name])
        return message_file.file.read()
