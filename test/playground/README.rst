Playground
==========
Scripts for simulating the default local/remote set up, adding new commits by
package. Used for creating disposable repositories to play with. Basically a
shell script version of the ``function_repo`` fixture.

``init.sh``
-----------
Create local repository, create remote and identify it as the “origin” of
local. Arguments are the package names. Usage example:

.. code-block:: bash

    $ ./init.sh pkg-a pkg-b
    Initialized empty Git repository in /Users/ben/work/tagging/tags/test/playground/repos/remote/.git/
    Initialized empty Git repository in /Users/ben/work/tagging/tags/test/playground/repos/local/.git/
    [master (root-commit) d933bca] a
     2 files changed, 2 insertions(+)
     create mode 100644 pkg-a/deploy
     create mode 100644 pkg-b/deploy
    $ tree repos
    repos
    ├── local
    │   ├── pkg-a
    │   │   └── deploy
    │   └── pkg-b
    │       └── deploy
    └── remote
    $ cd repos/local && git remote -v
    origin  /Users/ben/work/tagging/tags/test/playground/repos/remote (fetch)
    origin  /Users/ben/work/tagging/tags/test/playground/repos/remote (push)

``./touch.sh``
--------------
Modify a package and create a commit for it. Allows a new release to be cut.
Arguments are the package names. Usage example:


.. code-block:: bash

    $ ./touch.sh pkg-a
    [master 25761f8] Commit on Mon  4 May 2015 00:36:31 BST
     1 file changed, 1 insertion(+), 1 deletion(-)

``./cleanup.sh``
----------------
Just deletes everything under ``repos``. Saves a few keystrokes...
