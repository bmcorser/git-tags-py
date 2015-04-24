import traceback
from click.testing import CliRunner
import tags


def test_cli_basic(monkeypatch, function_repo):
    'The CLI runs'
    function_repo.packages('a', 'b')
    monkeypatch.setattr(tags.message, 'capture_message', lambda: 'User message')
    runner = CliRunner()
    result = runner.invoke(tags.cli.main, ['release', 'a', 'b'])
    assert result.exit_code == 0
