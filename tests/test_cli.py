from typer.testing import CliRunner
from gama.cli import app
from unittest.mock import patch

runner = CliRunner()

@patch("gama.cli.StateManager.run")
def test_scan(mock_run):
    mock_run.return_value = {"overall_status": "PASSED"}
    result = runner.invoke(app, ["scan"])
    assert result.exit_code == 0
    assert "Scanning Database..." in result.stdout

@patch("gama.cli.run_loop")
def test_loop(mock_run_loop):
    result = runner.invoke(app, ["loop"])
    assert result.exit_code == 0
    assert "Assessing current state..." in result.stdout

@patch("gama.cli.StateManager.run")
@patch("gama.cli.generate_audit_report")
def test_report(mock_generate_audit_report, mock_run):
    mock_run.return_value = {"overall_status": "PASSED", "aggregated_errors": []}
    result = runner.invoke(app, ["report"])
    assert result.exit_code == 0
    assert "Compiling audit data..." in result.stdout
