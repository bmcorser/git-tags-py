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
        self.channel = channel
        self.repo_path = repo_path

        self._packages = None
        self._changed_packages = None
        self._number = None
        self._channel_releases = None

    @property
    def number(self):
        if not self._number:
            channel_releases = lookup.channel_releases(self.channel)
            if channel_releases:
                self._number = int(channel_releases[0].split('/')[-1]) + 1
            else:
                self._number = 1
        return self._number

    @property
    def packages(self):
        if not self._packages:
            ret_dict = {}
            for name in lookup.packages(self.repo_path).keys():
                ret_dict[name] = git.path_tree(name)
            self._packages = ret_dict
        return self._packages

    @property
    def changed_packages(self):
        if not self._changed_packages:
            ret_dict = {}
            released = lookup.channel_releases(self.channel)
            if not released:
                return self.packages

            def look_back(name):
                for ref in released:
                    tree = git.tag_dict(ref)['body'].get(name)
                    if tree:
                        return tree

            previous_release = git.tag_dict(released[0])['body']

            for name, tree in self.packages.items():
                if name not in previous_release:
                    last_tree = look_back(name)
                else:
                    last_tree = previous_release[name]

                if tree != last_tree:
                    ret_dict[name] = tree
            self._changed_packages = ret_dict
        return self._changed_packages

    def create_tag(self):
        'Create the required tags for this release'
        try:
            ref = "releases/{0}/{1}".format(self.channel, self.number)
            git.create_tag(yaml.dump(self.changed_packages, default_flow_style=False), ref)
        except git.TagError as err_tag:
            fmt_error = "ERROR: Could not create tag {0}".format(err_tag)
            click.secho(fmt_error, fg='red', bold=True)
            click.secho('Attempting to clean up ...', fg='yellow')
            for tag in self.new_tags:
                git.delete_tag(tag)
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
