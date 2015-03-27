import traceback
from click.testing import CliRunner
import tags


def test_cli_basic(monkeypatch, session_repo):
    monkeypatch.setattr(tags.message, 'capture_message', lambda: 'User message')
    runner = CliRunner()
    result = runner.invoke(tags.cli.main, ['a', 'b'])
    assert result.exit_code == 0
