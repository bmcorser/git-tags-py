# git-tags-py

[![travis](https://travis-ci.org/bmcorser/git-tags-py.svg?branch=master)](https://travis-ci.org/bmcorser/git-tags-py)

Cut releases from a Git repo,

Designed for continuous deliveryish workflows, where releases are frequent.

## Setup
To define a directory as a package that will be recognised by `git-tags-py`,
add a `.package` file to that directory.

To set a default channel for releases set the environment variable
`GIT_TAGS_PY_CHANNEL`. This can be overriden with the `-c` flag.

## From the command line
Check out the
[playground](https://github.com/bmcorser/git-tags-py/tree/master/test/playground)
tutorial covering intended workflow, that’s probably the easiest way to get to
grips with command line usage. The “entrypoint” command is simply ``tag`` with
two subcommands ``release`` to cut new releases and ``lookup`` to inspect
historic release tags.

## `release`

```
tag release [-c <channel>] [-m <message>]
            [--force] [--no-remote] [--repo|-r <path>]
```

## `lookup`

```
tag lookup [--repo|-r] [--yaml|-y] [--list|-l] <channel> [number]
```

## From a Python script
The `lookup` and `release` modules expose the same functionality as the CLI,
but return Python data structures instead of printing things to the terminal.
If your current working directory is a Git repository, a simple example might
look like this:


``` python
>>> import tags
>>> repo = tags.git.Repo('.')
>>> release = Release(repo, 'development')
>>> release.changed
{'exec': '302bd6cd55732551cfa071f33159e6a8d989a38d'}
>>> release.unchanged
{'assets/jazzy': 'b3fb93c6dbb28de2585b3b2b786279d1f3f93610',
 'assets/muted': 'b3fb93c6dbb28de2585b3b2b786279d1f3f93610',
 'lib': '0a1be0ae95f18bdccc881dcbc912b2993c95abda'}
>>> release.create_tag()  # write release tag to the repo
```

Now let's look up the latest release on the `development` channel:

``` python
>>> lookup = tags.lookup.Lookup(repo, 'development')
>>> latest = lookup.latest()
>>> latest.number
4
>>> latest.data
{'body': {'packages': {'changed': {'exec': '302bd6cd55732551cfa071f33159e6a8d989a38d'},
   'unchanged': {'assets/jazzy': 'b3fb93c6dbb28de2585b3b2b786279d1f3f93610',
    'assets/muted': 'b3fb93c6dbb28de2585b3b2b786279d1f3f93610',
    'lib': '0a1be0ae95f18bdccc881dcbc912b2993c95abda'}}},
 'tag': 'release/development/4',
 'tagger_email': 'user@playground',
 'tagger_name': 'playground-user',
 'time': '1435576963',
 'timezone': '+0100'}
```

## Copy pasta :spaghetti:
Watch the magic unfold without typing a thing (depends the excellent
[pyenv](https://github.com/yyuu/pyenv)):

    git clone git@github.com:bmcorser/git-tags-py.git
    cd git-tags-py
    pyenv virtualenv 2.7.8 git-tags-py
    pyenv activate git-tags-py
    python setup.py install
    cd test/playground
    ./init lib exec
    tag release -c development -m 'Release me!' -r local
    ./touch pkg-a
    tag release -c development -m 'Big things!' -r local
    tag lookup development -r local -y
