import os
import click
from . import git


class Release(object):

    def __init__(self, commit, alias, pkgs):
        self.commit = commit
        self.alias = alias
        self.pkgs = pkgs

    def _tag(self, pkg):
        'Return the tag name for a package release'
        if self.alias:
            return "releases/{0}/{1}/{2}".format(self.alias, self.commit, pkg)
        else:
            return "releases/{0}/{1}".format(self.commit, pkg)

    @property
    def tags(self):
        'Return a list of strings for tags to be created for this release'
        return map(self._tag, self.pkgs)

    def validate_pkgs(self):
        'Validate all the packages we are releasing have a deploy script'
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
        fmt_warning = "WARNING: The {0} package has already been released at {1}"
        for pkg in self.pkgs:
            tag = self._tag(pkg)
            if tag in existing_tags:
                click.echo(fmt_warning.format(pkg, self.commit))
                if not click.confirm('Do you want to continue?'):
                    click.echo('Release cancelled.')
                    click.echo('Bye.')
                    exit(0)
            else:
                chkd_tags.append(tag)
        if not chkd_tags:
            click.echo('Nothing to release, cancelled.')
            click.echo('Bye.')
            exit(1)
        return chkd_tags
