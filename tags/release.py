# coding: utf-8

import os
import click
from . import git

class Release(object):

    _tags = None

    def __init__(self, commit, alias, pkgs):
        self.commit = commit
        self.alias = alias
        self.pkgs = pkgs

    @property
    def tags(self):
        'Return a list of strings for tags to be created for this release'
        if not self._tags:
            for pkg in self.pkgs:
                if self.alias:
                    aliased_tag = git.fmt_tag(pkg, self.commit, self.alias)
                    self._tags.append(aliased_tag)
                self._tags.append(git.fmt_tag(pkg, self.commit))
        return self._tags

    def validate_pkgs(self):
        'Validate all the packages we are releasing have a deploy script'
        return  # no validation for now
        for pkg in self.pkgs:
            if not os.path.isfile(os.path.join(pkg, 'deploy')):
                click.echo("{0} is not a valid package".format(pkg))
                click.echo('Bye.')
                exit(1)

    def check_existing(self):
        '''
        Check if any of the packages in this release have been released
        already. Do user interaction stuff to cancel if necc.
        '''
        chkd_tags = []
        existing_tags = git.get_tag_list()
        fmt_error = ('ERROR: The {0} package hasn’t changed since its last '
                     'release (at {1}).')
        for pkg in self.pkgs:
            last_release = git.get_head_sha1(pkg)
            tag = git.fmt_tag(pkg, last_release, None)
            if tag in existing_tags:
                click.echo(fmt_error.format(pkg, self.commit))
                click.echo('Release cancelled.')
                click.echo('Bye.')
                exit(1)
            else:
                chkd_tags.append(tag)
        if not chkd_tags:
            click.echo('Nothing to release, cancelled.')
            click.echo('Bye.')
            exit(1)
        return chkd_tags
