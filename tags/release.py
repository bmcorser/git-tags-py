# coding: utf-8

import os
import click
import yaml
from . import git
from . import lookup


class Release(object):
    'Object to hold data for release validation and methods for tag creation'

    previous = None

    _packages = None
    _diff = None

    def __init__(self, repo, channel):
        if not channel:
            raise Exception('Must provide a channel to release on')
        self.lookup = lookup.Lookup(repo, channel)

        historic = self.lookup.latest()
        if historic:
            self.previous = historic
            number = historic.number + 1
        else:
            number = 1

        self.ref_name = git.release_tag(channel, number)
        self.number = number
        self.channel = channel
        self.repo = repo

    @property
    def packages(self):
        'Get packages at HEAD'
        if not self._packages:
            self._packages = self.lookup.packages()
        return self._packages

    @property
    def diff(self):
        'Look up package changes'
        if not self._diff:
            diff_ = {
                'changed': {},
                'unchanged': {},
            }
            if not self.previous:
                diff_['changed'] = self.packages
            else:
                prev_pkgs = self.previous.data['body']['packages']
                released_pkgs = {}
                for name in ['changed', 'unchanged']:
                    released_pkgs.update(prev_pkgs[name])
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
        'Create the tag for this release'
        try:
            body_dict = {
                'packages': {
                    'changed': self.changed,
                    'unchanged': self.unchanged,
                }
            }
            body = yaml.dump(body_dict, default_flow_style=False)
            self.repo.create_tag(body, self.ref_name)
        except git.CreateTagError as err_tag:
            fmt_error = "ERROR: Could not create tag {0}".format(err_tag)
            click.secho(fmt_error, fg='red', bold=True)
            click.secho('Attempting to clean up ...', fg='yellow')
            self.repo.delete_tag(self.ref_name)
            click.echo('Bye.')
            exit(os.EX_CANTCREAT)
