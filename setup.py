from setuptools import setup

VERSION = '0.0.1'
ENTRY_POINTS = \
    '''
    [console_scripts]
    git-tags=tags.cli:main
    '''

setup(
    name='tags',
    version=VERSION,
    packages=['tags', 'tags/git'],
    install_requires=[
        'click',
        'six',
    ],
    entry_points=ENTRY_POINTS
)
