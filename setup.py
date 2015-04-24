from setuptools import setup

VERSION = '0.0.3'
DESC = 'CLI for managing release tags in a Git repository'
setup(
    name='git-tags',
    description=DESC,
    short_description=DESC,
    version=VERSION,
    packages=['tags'],
    install_requires=['click'],
    entry_points={'console_scripts': ['tag=tags.cli:main']}
)
