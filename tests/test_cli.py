from typer.testing import CliRunner
from gama.cli import app

runner = CliRunner()

def test_scan():
    result = runner.invoke(app, ["scan"])
    assert result.exit_code == 0
    assert "Scanning Database..." in result.stdout

def test_loop():
    result = runner.invoke(app, ["loop"])
    assert result.exit_code == 0
    assert "Assessing current state..." in result.stdout

def test_report():
    result = runner.invoke(app, ["report"])
    assert result.exit_code == 0
    assert "Compiling audit data..." in result.stdout
