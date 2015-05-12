git-tags-py
###########

.. image:: https://travis-ci.org/bmcorser/git-tags-py.svg?branch=master
    :target: https://travis-ci.org/bmcorser/git-tags-py

Designed for continuous deliveryish workflows, where releases are frequent.

From the command line
---------------------
There’s a playground_ for that, it’s probably the easiest way to get to grips
with command line usage. The “entrypoint” command is simply ``tag`` with two
subcommands ``release`` to cut new releases and ``lookup`` to inspect historic
release tags.

``release``
'''''''''''

.. code-block::

    tag release [<pkg>, [<pkg>, ...]] [-a <alias>] [-m <message>]
                [--force] [--no-remote] [--repo <path>]

``lookup``
''''''''''

.. code-block::

    tag lookup [<pkg>, [<pkg>, ...]] [-a <alias>|-c <commit>]
               [--repo] [--yaml]

.. _playground: https://github.com/bmcorser/git-tags-py/tree/master/test/playground

From a Python script
--------------------
The ``lookup`` and ``release`` modules expose the same functionality as the
CLI, but return Python data structures instead of printing things to the
terminal. If your current working directory is a Git repository, a simple
example might look like this:

.. code-block:: python

    >>> from tags import git
    >>> from tags.release import Release
    >>> release = Release(git.head_abbrev(), None, ['pkg-a', 'pkg-b'])
    >>> release.notes = ‘My test release’
    >>> release.pkgs
    ['pkg-a', 'pkg-b']
    >>> release.new_tags
    {'releases/pkg-a/85a4b16', 'releases/pkg-b/85a4b16'}
    >>> release.create_tags()  # write tags to the repo

Now let's look up the release by package name:

.. code-block:: python

    >>> from tags import lookup
    >>> lookup.package('pkg-a')
    [{'message': 'My test release',
      'tag': 'releases/pkg-a/85a4b16',
      'tagger_email': 'user@playground',
      'tagger_name': 'playground-user',
      'time': '1431374444',
      'timezone': '+0100'}]

Copy pasta :spaghetti:
----------------------
Watch the magic unfold without typing a thing (depends the excellent pyenv_)::

    git clone git@github.com:bmcorser/git-tags-py.git
    cd git-tags-py
    pyenv virtualenv 2.7.8 !$
    pyenv activate !$
    python setup.py install
    cd test/playground
    ./init pkg-a pkg-b
    tag release pkg-a -m 'Release me!' --repo local
    ./touch pkg-a
    tag release \* -m 'Just release whatever' --repo local
    tag lookup pkg-a --repo local --yaml

.. _pyenv: https://github.com/yyuu/pyenv
