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

.. _playground: https://github.com/bmcorser/git-tags-py/tree/master/test/playground

From a Python script
--------------------
The ``lookup`` and ``release`` modules expose the same functionality as the
CLI, but return Python data structures instead of printing things to the
terminal. If your current working directory is a Git repoistory, a simple
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
