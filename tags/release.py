# coding: utf-8

import os
import click
import yaml
from . import git
from . import lookup


def is_pkg(repo_path, pkg):
    'Return bool of whether passed directory name is a package'
    for name in ('deploy', 'build'):
        if not os.path.isfile(os.path.join(repo_path, pkg, name)):
            return False
    return True


def validate_pkgs(pkgs):
    'Validate all the packages we are releasing have a deploy script'
    for pkg in pkgs:
        if not is_pkg(pkg):
            click.secho("ERROR: {0} is not a valid package".format(pkg),
                        fg='red', bold=True)
            click.echo('Bye.')
            exit(os.EX_DATAERR)


class Release(object):
    'Object to hold data for release validation and methods for tag creation'

    def __init__(self, repo_path, channel):
        if not channel:
            raise Exception('Must provide a channel to release on')
        head = git.head_abbrev()
        repo_root = git.repo_root(repo_path)
        self.lookup = lookup.Lookup(repo_root, head, channel)

        history = self.lookup.releases()
        if history:
            number = int(history[0].split('/')[-1]) + 1
        else:
            number = 1

        self.ref_name = git.release_tag(channel, number)
        self.number = number
        self.channel = channel
        self.target = head

        self._packages = None
        self._diff = None
        self._channel_releases = None

    @property
    def packages(self):
        if not self._packages:
            self._packages = self.lookup.packages(self.target)
        return self._packages

    @property
    def diff(self):
        'Look up package changes'
        if not self._diff:
            diff_ = {
                'changed': {},
                'unchanged': {},
            }
            released = self.lookup.latest()
            if not released:
                diff_['changed'] = self.packages
            else:
                released_pkgs = {}
                for name in ['changed', 'unchanged']:
                    released_pkgs.update(released['body']['packages'][name])
                for name, tree in self.packages.items():
                    if name not in released_pkgs:
                        diff_['changed'][name] = tree
                        continue
                    if tree == released_pkgs[name]:
                        diff_['unchanged'][name] = tree
                    else:
                        diff_['changed'][name] = tree
            self._diff = diff_
        return self._diff

    @property
    def changed(self):
        'Which packages changed since the last release'
        return self.diff['changed']

    @property
    def unchanged(self):
        'Which packages remain unchanged since the last release'
        return self.diff['unchanged']

    def create_tag(self):
        'Create the required tags for this release'
        try:
            body_dict = {
                'packages': {
                    'changed': self.changed,
                    'unchanged': self.unchanged,
                }
            }
            git.create_tag(yaml.dump(body_dict, default_flow_style=False),
                           self.ref_name)
        except git.TagError as err_tag:
            fmt_error = "ERROR: Could not create tag {0}".format(err_tag)
            click.secho(fmt_error, fg='red', bold=True)
            click.secho('Attempting to clean up ...', fg='yellow')
            git.delete_tag(ref_name)
            click.echo('Bye.')
            exit(os.EX_CANTCREAT)

    def validate_unreleased(self):
        '''
        Check if any of the packages in this release have been released
        already. Exit if they have.
        '''
        chkd_tags = []
        fmt_error = ('ERROR: The {0} package hasn’t changed since its last '
                     'release (at {1}).')
        for pkg in self.pkgs:
            released_as = self.released(pkg)
            if released_as:
                click.secho(fmt_error.format(pkg, released_as),
                            fg='red', bold=True)
                click.echo('Release cancelled.')
                click.echo('Bye.')
                exit(os.EX_USAGE)
            else:
                chkd_tags.append(git.fmt_tag(pkg, self.commit, self.alias))
        if not chkd_tags:
            click.echo('Nothing to release, cancelled.')
            click.echo('Bye.')
            exit(os.EX_USAGE)
        return chkd_tags

    def _unreleased_packages(self):
        'Return a list of unreleased packages'
        unreleased_pkgs = []
        for pkg in filter(self.is_pkg, os.listdir('.')):
            if not self.released(pkg):
                unreleased_pkgs.append(pkg)
        if not unreleased_pkgs:
            click.echo('No packages have changed since last release')
            exit(os.EX_DATAERR)
        return unreleased_pkgs
