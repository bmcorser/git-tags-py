from setuptools import setup

VERSION = '0.0.3'
DESC = 'CLI for managing release tags in a Git repository'
setup(
    name='git-tags',
    description=DESC,
    author='bmcorser',
    author_email='bmcorser@gmail.com',
    short_description=DESC,
    version=VERSION,
    packages=['tags', 'tags.cli'],
    install_requires=['click', 'pyyaml'],
    entry_points={'console_scripts': ['tag=tags.cli.main:command_group']}
)
