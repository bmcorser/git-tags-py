from setuptools import setup

VERSION = '0.1.8'
DESC = 'CLI for managing release tags in a Git repository'
URL = 'https://github.com/bmcorser/git-tags-py'
setup(
    name='git-tags',
    url=URL,
    long_description="{0}, see {1} for more information.".format(DESC, URL),
    author='bmcorser',
    author_email='bmcorser@gmail.com',
    description=DESC,
    version=VERSION,
    packages=['tags', 'tags.cli'],
    install_requires=['click', 'pyyaml', 'arrow'],
    entry_points={'console_scripts': ['tag=tags.cli.main:command_group']}
)
