from setuptools import setup

VERSION = '0.0.2'
ENTRY_POINTS = \
    '''
    [console_scripts]
    tag=tags.cli:main
    '''

setup(
    name='tag',
    version=VERSION,
    packages=['tags'],
    install_requires=['click'],
    entry_points=ENTRY_POINTS
)
