from datetime import datetime

import pytest
import responses
from responses import matchers

from medium_stats import StatGrabberPublication
from medium_stats.utils import convert_datetime_to_unix
from tests.mocks.mock_data import mock_metadata
from tests.mocks.mock_data import mock_story_summary_stats
from tests.mocks.mock_responses import mock_homepage
from tests.mocks.mock_responses import mock_summary_stats
from tests.mocks.mock_responses import mock_views
from tests.mocks.mock_responses import mock_visitors


@responses.activate
def test_init_gets_metadata(publication_config):
    responses.add(responses.GET, "https://medium.com/foo-blog", body=mock_homepage())

    sg = StatGrabberPublication(**publication_config)
    metadata = mock_metadata()
    assert sg.id == metadata["id"]
    assert sg.slug == metadata["slug"]
    assert sg.name == metadata["name"]
    assert sg.creator == metadata["creatorId"]
    assert sg.description == metadata["description"]
    assert sg.domain == metadata["domain"]
    assert sg.collections_endpoint == f"https://medium.com/_/api/collections/{sg.id}/stats"


@responses.activate
def test_init_without_domain_imputes_none(publication_config):
    responses.add(responses.GET, "https://medium.com/foo-blog", body=mock_homepage(domain=False))
    sg = StatGrabberPublication(**publication_config)
    assert sg.domain is None


@responses.activate
@pytest.mark.parametrize(
    "event_type, mock_body, expected_keys",
    [
        ("views", mock_views, ("timeWindowStart", "ttrMs", "views")),
        ("visitors", mock_visitors, ("timeWindowStart", "dailyUniqueVisitors")),
    ],
)
def test_get_events_views(event_type, mock_body, expected_keys, publication_config):
    start = datetime(2021, 10, 4)
    stop = datetime(2021, 10, 5)
    start_ts, stop_ts = map(convert_datetime_to_unix, (start, stop))

    responses.add(responses.GET, "https://medium.com/foo-blog", body=mock_homepage())
    sg = StatGrabberPublication(**publication_config)

    url = "/".join([sg.collections_endpoint, event_type])
    params = {"from": str(start_ts), "to": str(stop_ts)}
    responses.add(
        responses.GET, url, body=mock_body(), match=[matchers.query_param_matcher(params)], match_querystring=False
    )
    data = sg.get_events(start, stop, type_=event_type)

    assert isinstance(data, list)
    assert all(key in record for record in data for key in expected_keys)


@responses.activate
def test_get_summary_stats(publication_config):
    responses.add(responses.GET, "https://medium.com/foo-blog", body=mock_homepage())
    sg = StatGrabberPublication(**publication_config)
    responses.add(responses.GET, f"https://medium.com/{sg.slug}/stats/stories?limit=50", body=mock_summary_stats())
    data = sg.get_summary_stats()

    assert isinstance(data, list)
    assert data == mock_story_summary_stats()
