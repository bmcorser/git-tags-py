Playground
==========
Scripts for simulating the default local/remote set up, adding new commits by
package. Used for creating disposable repositories to play with. Basically a
shell script version of the ``function_repo`` fixture.

Creating a playground
---------------------
The ``init.sh`` script will create a ``local`` repository then create a
``remote`` repository and identify it as the “origin” of local. Arguments are
the package names. Usage example:

.. code-block:: plain

    $ ./init.sh pkg-a pkg-b
    # ...
    $ tree local
    local
    ├── pkg-a
    │   └── deploy
    └── pkg-b
        └── deploy

    2 directories, 2 files
    $ cd local
    $ git remote -v
    origin  .../test/playground/remote (fetch)
    origin  .../test/playground/remote (push)

Paths are truncated for brevity. We can see that the “packages” supplied to
``./init.sh`` have been created in the local repo and the remote repo is set as
its origin (the default remote).

Playing with the CLI
--------------------
Now the playground repos are set up we can cut a release for one of the
packages we created and see it bears the abbreviated commit seen above. Be sure
to specify the playground repo with ``--repo local`` otherwise a release tag
will be added to the parent repo, which is probably not what you want here:

.. code-block:: plain

    $ tag release pkg-a -m 'Toy release' --repo local
    Release notes:
      Toy release
    Release name:
      980f48c
    Packages included in this release:
      pkg-a
    Tags created:
      releases/pkg-a/980f48c
    Bye.

We can release the same version of a package under an alias, using the ``-a``
option:

.. code-block:: plain

    $ tag release pkg-a -a special-alias -m 'Aliased release' --repo local
    Release notes:
      Aliased release
    Release alias:
      special-alias
    Packages in this alias:
      pkg-a
    Tags created:
      releases/special-alias/pkg-a/980f48c
    Bye.


Cutting more releases
---------------------
Since releases are bound to Git commits, it is not possible create more than
one release for any given commit unless releasing under an alias. The
``touch.sh`` script will create a new commit for the passed package(s),
allowing a new release to be cut.  Usage example:

.. code-block:: plain

    $ ./touch.sh pkg-a
    [master 25761f8] Commit on Mon  4 May 2015 00:36:31 BST
     1 file changed, 1 insertion(+), 1 deletion(-)

Examining release history
-------------------------
We can see the releases we created using the ``lookup`` subcommand; quering by
package, release name (commit) or alias. At the moment only YAML printing is
available, which must be specified with the ``--yaml`` flag. Again, don’t
forget to use ``--repo local`` to specify the local repo. Let’s create a new
commit for ``pkg-a`` and release it again, then get some YAML to show the
release history:

.. code-block:: plain

    $ ./touch.sh pkg-a
    $ tag release pkg-a -m 'Next release' --repo local
    $ tag lookup pkg-a --repo local --yaml
    pkg-a:
    - message: Next release
      tag: releases/pkg-a/c3b8dd6
    - message: Toy release
      tag: releases/pkg-a/980f48c
      timezone: '+0100'


Starting over
-------------
If you get sick of the package names you’ve chosen and want to start over, the
``cleanup.sh`` will delete the local and remote repos. It could even you save a
few keystrokes...
