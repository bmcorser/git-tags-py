from setuptools import setup

VERSION = '0.0.2'
ENTRY_POINTS = \
    '''
    [console_scripts]
    tags=tags.cli:main
    '''

setup(
    name='tags',
    version=VERSION,
    packages=['tags'],
    install_requires=['click'],
    entry_points=ENTRY_POINTS
)
