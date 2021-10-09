from datetime import datetime
from datetime import timezone

import responses
from responses import matchers

from medium_stats.scraper import StatGrabberBase
from medium_stats.scraper.queries import get_chart_query
from medium_stats.scraper.queries import get_referrer_query
from medium_stats.utils import convert_datetime_to_unix
from tests.mocks.mock_responses import mock_chart_response_body
from tests.mocks.mock_responses import mock_referrer_response_body


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
    assert "post" in data.keys()
    daily_stats = data["post"]["dailyStats"]
    assert all(key in record for record in daily_stats for key in ("periodStartedAt", "memberTtr", "views"))
    assert all(start_ts <= day["periodStartedAt"] < stop_ts for day in daily_stats)


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
    assert "post" in data.keys()
    referrers = data["post"]["referrers"]
    assert all(key in record for record in referrers for key in ("platform", "sourceIdentifier", "totalCount"))
