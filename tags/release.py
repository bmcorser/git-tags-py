# coding: utf-8

import os
import click
from . import git


class Release(object):

    def __init__(self, commit, alias, pkgs):
        self._tags = []
        self._existing_tags = None
        self._new_tags = []
        self.notes = ''

        self.commit = commit
        self.alias = alias
        self.pkgs = pkgs

    @property
    def existing_tags(self):
        'Return the set of existing tags'
        if not self._existing_tags:
            self._existing_tags = set(git.get_tag_list())
        return self._existing_tags

    @property
    def tags(self):
        'Return a list of strings for tags to be created for this release'
        if not self._tags:
            tags_list = []
            for pkg in self.pkgs:
                if self.alias:
                    aliased_tag = git.fmt_tag(pkg, self.commit, self.alias)
                    tags_list.append(aliased_tag)
                tags_list.append(git.fmt_tag(pkg, self.commit, None))
            self._tags = set(tags_list)
        return self._tags

    @property
    def new_tags(self):
        'Return a list of the new tags for this release'
        if not self.alias:
            return self.tags
        alias_frag = "/{0}/".format(self.alias)
        non_alias_tags = set()
        for tag in self.tags:
            if alias_frag not in tag and tag not in self.existing_tags:
                non_alias_tags.add(tag)
        alias_tags = set(filter(lambda tag: alias_frag in tag, self.tags))
        return non_alias_tags | alias_tags

    def create_tags(self):
        'Create the required tags for this release'
        for tag in self.new_tags:
            try:
                git.create_tag(self.notes, tag)
            except git.TagError as err_tag:
                fmt_error = "ERROR: Could not create tag {0}".format(err_tag)
                click.secho(fmt_error, fg='red', bold=True)
                click.secho('Attempting to clean up ...', fg='yellow')
                for tag in self.new_tags:
                    git.delete_tag(tag)
                click.echo('Bye.')
                exit(os.EX_CANTCREAT)

    def validate_pkgs(self):
        'Validate all the packages we are releasing have a deploy script'
        for pkg in self.pkgs:
            if not os.path.isfile(os.path.join(pkg, 'deploy')):
                click.echo("{0} is not a valid package".format(pkg))
                click.echo('Bye.')
                exit(os.EX_DATAERR)

    def check_existing(self):
        '''
        Check if any of the packages in this release have been released
        already.
        '''
        chkd_tags = []
        fmt_error = ('ERROR: The {0} package hasn’t changed since its last '
                     'release (at {1}).')
        for pkg in self.pkgs:
            last_release = git.get_head_sha1(pkg)[:7]
            pkg_tag = git.fmt_tag(pkg, last_release, self.alias)
            tag = git.fmt_tag(pkg, self.commit, self.alias)
            if tag in self.existing_tags or pkg_tag in self.existing_tags:
                click.secho(fmt_error.format(pkg, self.commit),
                            fg='red', bold=True)
                click.echo('Release cancelled.')
                click.echo('Bye.')
                exit(os.EX_USAGE)
            else:
                chkd_tags.append(tag)
        if not chkd_tags:
            click.echo('Nothing to release, cancelled.')
            click.echo('Bye.')
            exit(os.EX_USAGE)
        return chkd_tags
