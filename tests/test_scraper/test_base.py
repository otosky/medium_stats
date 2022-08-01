from datetime import datetime
from datetime import timezone

import responses
from responses import matchers

from medium_stats.scraper import StatGrabberBase
from medium_stats.scraper.queries import get_chart_query
from medium_stats.scraper.queries import get_referrer_query
from medium_stats.utils import convert_datetime_to_unix
from tests.mocks.mock_data import mock_story_summary_stats
from tests.mocks.mock_responses import mock_chart_response_body
from tests.mocks.mock_responses import mock_referrer_response_body


def test_get_article_ids(config):
    sg = StatGrabberBase(**config)
    article_ids = sg.get_article_ids(mock_story_summary_stats())

    expected_ids = [mock_story_summary_stats()[0]["postId"]]
    assert len(article_ids) == 1
    assert article_ids == expected_ids
    assert sg.articles == expected_ids


@responses.activate
def test_get_view_read_totals(config):
    start = datetime(2021, 10, 5, tzinfo=timezone.utc)
    stop = datetime(2021, 10, 6, tzinfo=timezone.utc)
    start_ts = convert_datetime_to_unix(start)
    stop_ts = convert_datetime_to_unix(stop)
    post_id = "id-string"
    sg = StatGrabberBase(**config)

    gql_query = get_chart_query(post_id, start, stop)
    responses.add(
        responses.POST,
        sg.gql_endpoint,
        body=mock_chart_response_body(),
        match=[matchers.json_params_matcher(gql_query)],
    )

    data = sg.get_view_read_totals(post_id, start, stop)
    assert isinstance(data, dict)
    assert "id" in data.keys()
    daily_stats = data["dailyStats"]
    assert all(key in record for record in daily_stats for key in ("periodStartedAt", "memberTtr", "views"))
    assert all(start_ts <= day["periodStartedAt"] < stop_ts for day in daily_stats)


def test_get_all_view_read_totals(config, mocker):
    start = datetime(2021, 10, 5, tzinfo=timezone.utc)
    stop = datetime(2021, 10, 6, tzinfo=timezone.utc)
    sg = StatGrabberBase(**config)
    mock_method = mocker.MagicMock()
    mocker.patch.object(sg, "get_view_read_totals", mock_method)
    sg.get_all_view_read_totals(post_ids=range(5), start=start, stop=stop)

    assert mock_method.call_count == 5


@responses.activate
def test_referrer_totals(config):
    post_id = "id-string"
    sg = StatGrabberBase(**config)

    gql_query = get_referrer_query(post_id)
    responses.add(
        responses.POST,
        sg.gql_endpoint,
        body=mock_referrer_response_body(),
        match=[matchers.json_params_matcher(gql_query)],
    )

    data = sg.get_referrer_totals(post_id)
    assert isinstance(data, dict)
    assert "id" in data.keys()
    referrers = data["referrers"]
    assert all(key in record for record in referrers for key in ("platform", "sourceIdentifier", "totalCount"))


def test_get_all_referrer_totals(config, mocker):
    sg = StatGrabberBase(**config)
    mock_method = mocker.MagicMock()
    mocker.patch.object(sg, "get_referrer_totals", mock_method)
    sg.get_all_referrer_totals(post_ids=range(5))

    assert mock_method.call_count == 5
