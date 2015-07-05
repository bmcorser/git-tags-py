from click.testing import CliRunner
import traceback
import tags


def test_cli_basic(fn_repo):
    'The CLI runs'
    fn_repo.packages('a', 'b')
    runner = CliRunner()
    result = runner.invoke(tags.cli.command_group, [
        'release',
        '-c', 'test',
        '-m', 'test release',
        '-r', fn_repo.local
    ])
    assert result.exit_code == 0
