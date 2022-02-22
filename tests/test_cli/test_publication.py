import pytest
from typer.testing import CliRunner

from medium_stats.cli.core import fmt_json
from medium_stats.cli.publication import publication_app
from medium_stats.utils import select_keys
from tests.mocks.mock_data import mock_article_daily_view_reads
from tests.mocks.mock_data import mock_events__views
from tests.mocks.mock_data import mock_events__visitors
from tests.mocks.mock_data import mock_referrer_totals
from tests.mocks.mock_data import mock_story_summary_stats

runner = CliRunner()


@pytest.mark.parametrize(
    "to_patch,mocked_data,cli_command",
    [
        ("get_summary_stats", mock_story_summary_stats, ("summary",)),
        ("get_events", mock_events__views, ("events-views", "2021-10-05", "2021-10-06")),
        ("get_events", mock_events__visitors, ("events-visitors", "2021-10-05", "2021-10-06")),
    ],
)
def test_get_summary(mocker, to_patch, mocked_data, cli_command):
    mock = mocker.patch(f"medium_stats.cli.publication.StatGrabberPublication.{to_patch}", return_value=mocked_data())
    result = runner.invoke(publication_app, [*cli_command])
    assert mock.called

    assert result.exit_code == 0
    assert result.stdout == fmt_json(mocked_data()) + "\n"


@pytest.mark.parametrize(
    "to_patch,mocked_data,cli_command",
    [
        ("get_view_read_totals", mock_article_daily_view_reads, ("articles", "2021-10-05", "2021-10-06")),
        ("get_referrer_totals", mock_referrer_totals, ("referrers",)),
    ],
)
def test_get_stats_for_all_articles(mocker, to_patch, mocked_data, cli_command):

    mocker.patch(f"medium_stats.cli.publication.StatGrabberPublication.get_summary_stats")
    mocker.patch(f"medium_stats.cli.publication.StatGrabberPublication.get_article_ids", return_value=["id-string"])
    mock = mocker.patch(f"medium_stats.cli.publication.StatGrabberPublication.{to_patch}", return_value=mocked_data())
    result = runner.invoke(publication_app, [*cli_command])
    assert mock.called

    assert result.exit_code == 0
    assert result.stdout == fmt_json([mocked_data()]) + "\n"


def test_get_article_ids(mocker):
    summary_data = mock_story_summary_stats()
    mock = mocker.patch(
        f"medium_stats.cli.publication.StatGrabberPublication.get_summary_stats", return_value=summary_data
    )
    result = runner.invoke(publication_app, ["get-article-ids"])
    assert mock.called

    assert result.exit_code == 0
    expected_data = [select_keys({"postId", "title"}, post) for post in summary_data]
    assert result.stdout == fmt_json(expected_data) + "\n"
