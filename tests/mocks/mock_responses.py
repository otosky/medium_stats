import json

from tests.mocks.mock_data import mock_article_daily_view_reads
from tests.mocks.mock_data import mock_events__views
from tests.mocks.mock_data import mock_events__visitors
from tests.mocks.mock_data import mock_metadata
from tests.mocks.mock_data import mock_referrer_totals
from tests.mocks.mock_data import mock_story_summary_stats


def format_mock_response_body(payload):
    js_prefix = "])}while(1);</x>"
    data = {"success": True, "payload": payload}
    return (js_prefix + json.dumps(data)).encode()


def mock_homepage(domain=True):
    metadata = mock_metadata() if domain else {k: v for k, v in mock_metadata().items() if k != "domain"}
    payload = {"collection": metadata}
    return format_mock_response_body(payload)


def mock_chart_response_body():
    payload = {"data": {"post": mock_article_daily_view_reads()}}
    return json.dumps(payload).encode()


def mock_referrer_response_body():
    payload = {"data": {"post": mock_referrer_totals()}}
    return json.dumps(payload).encode()


def mock_views():
    payload = {"value": mock_events__views()}
    return format_mock_response_body(payload)


def mock_visitors():
    payload = {"value": mock_events__visitors()}
    return format_mock_response_body(payload)


def mock_summary_stats():
    payload = {"value": mock_story_summary_stats()}
    return format_mock_response_body(payload)
