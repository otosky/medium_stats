from datetime import datetime
from itertools import chain
from itertools import repeat

import responses

from medium_stats import StatGrabberUser
from medium_stats.utils import convert_datetime_to_unix
from tests.mocks.mock_data import mock_story_summary_stats
from tests.mocks.mock_responses import mock_summary_stats
from tests.mocks.mock_responses import mock_views


@responses.activate
def test_get_events(user_config):
    """Events for User stats are only `views` - there are no stats for `visitors`."""
    start = datetime(2021, 10, 4)
    stop = datetime(2021, 10, 5)
    start_ts, stop_ts = map(convert_datetime_to_unix, (start, stop))

    sg = StatGrabberUser(**user_config)

    url = sg._get_events_url(start_ts, stop_ts)
    responses.add(responses.GET, url, body=mock_views())
    data = sg.get_events(start, stop)

    assert isinstance(data, list)
    expected_keys = ("timeWindowStart", "ttrMs", "views")
    assert all(key in record for record in data for key in expected_keys)


@responses.activate
def test_get_summary_stats(user_config):
    sg = StatGrabberUser(**user_config)
    responses.add(responses.GET, sg._base_url, body=mock_summary_stats())
    data = sg.get_summary_stats()

    assert isinstance(data, list)
    assert data == mock_story_summary_stats()


@responses.activate
def test_get_summary_stats_paginated(user_config):
    sg = StatGrabberUser(**user_config)
    responses.add(responses.GET, sg._base_url, body=mock_summary_stats(paginated=True))
    responses.add(responses.GET, sg._base_url, body=mock_summary_stats(paginated=False))
    data = sg.get_summary_stats(limit=1)

    assert isinstance(data, list)
    assert data == list(chain.from_iterable(repeat(mock_story_summary_stats(), 2)))
