# coding: utf-8
from click.testing import CliRunner
import tags
from tags import git
import yaml
import uuid


def test_sharenotes(fn_repo):
    'Scenario where two users release against same commit'
    packages = (uuid.uuid4().hex, uuid.uuid4().hex)
    map(fn_repo.commit, packages)
    map(fn_repo.commit, packages)

    # should set both repos to the same commit
    git.run(fn_repo.local, ['push', 'origin'])
    git.run(fn_repo.local_other, ['pull', 'origin'])

    runner = CliRunner()

    # tarquin releases in his repo as 'test'
    tarquin_release = runner.invoke(tags.cli.command_group, [
        'release',
        '-c', 'test',
        '-m', 'a',
        '-r', fn_repo.local,
    ])
    assert tarquin_release.exit_code is 0

    # tony releases in his repo as 'tiger'
    tony_release = runner.invoke(tags.cli.command_group, [
        'release',
        '-c', 'tiger',
        '-m', 'a',
        '-r', fn_repo.local_other,
    ])
    assert tony_release.exit_code is 0


    # tarquin releases once more, as 'radical'
    tarquin_release_again = runner.invoke(tags.cli.command_group, [
        'release',
        '-c', 'radical',
        '-m', 'a',
        '-r', fn_repo.local,
    ])
    assert tarquin_release_again.exit_code is 0

    # tony looks up tarquin’s release
    tony_lookup = runner.invoke(tags.cli.command_group, [
        'lookup', 'radical', '-y', '-r', fn_repo.local_other,
    ])
    assert tony_lookup.exit_code is 0

    changed = yaml.load(tony_lookup.output)['body']['packages']['changed']
    for package in packages:
        assert package in changed
