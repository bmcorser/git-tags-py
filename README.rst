git-tags-py
###########

.. image:: https://travis-ci.org/bmcorser/git-tags-py.svg?branch=master
    :target: https://travis-ci.org/bmcorser/git-tags-py

Designed for continuous delivery workflows, where releases are frequent.

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
terminal.
