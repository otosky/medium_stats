from typer.testing import CliRunner

from medium_stats.cli.main import app

runner = CliRunner()

CLI_GROUPS = {"scrape-user", "scrape-publication"}


def test_cli_groups_are_registered():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cli in CLI_GROUPS:
        assert cli in result.stdout
