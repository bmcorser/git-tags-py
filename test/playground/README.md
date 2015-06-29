# Playground

Scripts for simulating the default local/remote set up, adding new commits by
package. Used for creating disposable repositories to play with. Basically a
shell script version of the
[`function_repo`](https://github.com/bmcorser/git-tags-py/blob/master/test/conftest.py#L84)
fixture.

## Creating a playground

The `./init` script will create a `local` repository then create a `remote`
repository and identify it as the “origin” of local. Arguments relative paths
to package directories. Usage example:

``` shell
$ ./init exec lib assets/jazzy assets/muted
$ tree -aI .git local
local
├── assets
│   ├── jazzy
│   │   └── .package
│   └── muted
│       └── .package
├── exec
│   └── .package
└── lib
    └── .package
$ cd local
$ git remote -v
origin  .../test/playground/remote (fetch)
origin  .../test/playground/remote (push)
```

Paths are truncated for brevity. We can see that the “packages” supplied to
`./init` have been created in the local repo and the remote repo is set as its
origin (the default remote).

## Playing with the CLI
Now the playground repos are set up we can cut a release for one of the
packages we created and see it bears the abbreviated commit seen above. Be sure
to specify the playground repo `local` with `--repo` or `-r` otherwise a
release tag will be added to the parent repo, which is probably not what you
want here:

``` shell
$ tag release -m 'Toy release' -r local

Release #1 on channel development

Included:
  lib
  assets/muted
  assets/jazzy
  exec

Tag: release/development/1

```

We can make the same release on a different channel, using the `-c` option:

``` shell
$ tag release -c production -m 'Toy release' -r local

Release #1 on channel production

Included:
  lib
  assets/muted
  assets/jazzy
  exec

Tag: release/production/1
```

## Cutting more releases
Since releases are bound to Git commits, it is not possible create more than
one release for any given commit unless releasing on a different channel. The
``./touch`` script will create a new commit for the passed package(s), allowing
a new release to be cut. Usage example:

``` shell
$ ./touch lib exec
[master 7d328d1] Commit on Mon Jun 29 11:16:20 BST 2015
 2 files changed, 2 insertions(+), 2 deletions(-)
```

It will now be possible to cut another release, as follows:

``` shell
$ tag release -m 'Pivot!' -r local

Release #2 on channel development

Included:
  lib
  exec

Tag: release/development/2
```

## Examining release history
We can see the releases we created using the ``lookup`` subcommand; quering by
channel and optionally number. Let’s look up the release we just made on the
`development` channel:

``` shell
$ tag lookup development -r local

Release #2 on channel development

Changed:
  lib
  exec

Unchanged:
  assets/muted
  assets/jazzy

Notes:
Pivot!
```


## Starting over
If you get sick of the package names you’ve chosen and want to start over, the
``./cleanup`` will delete the local and remote repos. It could even you save a
few keystrokes...
