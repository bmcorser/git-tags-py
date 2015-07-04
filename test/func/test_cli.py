from click.testing import CliRunner
import traceback
import tags


def test_cli_basic(function_repo):
    'The CLI runs'
    function_repo.packages('a', 'b')
    runner = CliRunner()
    result = runner.invoke(tags.cli.command_group, [
        'release',
        '-c', 'test',
        '-m', 'test release',
        '-r', function_repo.local
    ])
    assert result.exit_code == 0
