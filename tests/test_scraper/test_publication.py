import json
from datetime import datetime

import pytest
import responses

from medium_stats import StatGrabberPublication
from medium_stats.utils import convert_datetime_to_unix


def mock_metadata():
    return {
        "id": "asdflkjbasdl3",
        "name": "Foo Blog",
        "slug": "foo-blog",
        "tags": ["FOO", "PYTHON"],
        "creatorId": "abcdefg",
        "description": "The best in Foo, all the foo time.",
        "shortDescription": "Foo thoughts",
        "image": {
            "imageId": "abcde.png",
            "filter": "",
            "backgroundSize": "",
            "originalWidth": 300,
            "originalHeight": 296,
            "strategy": "resample",
            "height": 0,
            "width": 0,
        },
        "metadata": {"followerCount": 666, "activeAt": 1633456119462},
        "publicEmail": "foo@foo-blog.com",
        "domain": "foo.blog.com",
    }


def format_mock_response_body(payload):
    js_prefix = "])}while(1);</x>"
    data = {"success": True, "payload": payload}
    return (js_prefix + json.dumps(data)).encode()


def mock_homepage(domain=True):
    metadata = mock_metadata() if domain else {k: v for k, v in mock_metadata().items() if k != "domain"}
    payload = {"collection": metadata}
    return format_mock_response_body(payload)


def mock_views():
    payload = {
        "value": [
            {"timeWindowStart": 1633320000000, "ttrMs": 136008, "views": 1},
            {"timeWindowStart": 1633323600000, "ttrMs": 232381, "views": 3},
            {"timeWindowStart": 1633327200000, "ttrMs": 1001836, "views": 10},
        ]
    }
    return format_mock_response_body(payload)


def mock_visitors():
    # I'm not sure I understand this metric - how is it dailyUnique if each bucket is hourly?
    payload = {
        "value": [
            {"timeWindowStart": 1633320000000, "dailyUniqueVisitors": 83},
            {"timeWindowStart": 1633323600000, "dailyUniqueVisitors": 81},
            {"timeWindowStart": 1633327200000, "dailyUniqueVisitors": 83},
        ]
    }
    return format_mock_response_body(payload)


def mock_story_summary_stats():
    return {
        "claps": 100,
        "collectionId": "asdflkjasdlkj",
        "createdAt": 1632354904050,
        "creatorId": "jxb73b997b12",
        "firstPublishedAt": 1633456109000,
        "firstPublishedAtBucket": "2021",
        "friendsLinkViews": 0,
        "internalReferrerViews": 21,
        "isSeries": False,
        "postId": "123456567",
        "previewImage": {
            "alt": "Lorem ipsum",
            "id": "qwertyuiop.png",
            "isFeatured": True,
            "originalHeight": 600,
            "originalWidth": 1867,
        },
        "readingTime": 5,
        "reads": 41,
        "slug": "foo-thoughts-for-unhappy-times",
        "syndicatedViews": 2,
        "title": "Foo Thoughts For Unhappy Times",
        "type": "PostStat",
        "updateNotificationSubscribers": 0,
        "upvotes": 0,
        "views": 71,
        "visibility": 0,
    }


def mock_summary_stats():
    payload = {"value": [mock_story_summary_stats()]}
    return format_mock_response_body(payload)


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
def test_get_events_views(publication_config):
    start = datetime(2021, 10, 4)
    stop = datetime(2021, 10, 5)
    start_ts = convert_datetime_to_unix(start)
    stop_ts = convert_datetime_to_unix(stop)

    responses.add(responses.GET, "https://medium.com/foo-blog", body=mock_homepage())
    sg = StatGrabberPublication(**publication_config)
    responses.add(responses.GET, sg.collections_endpoint + f"/views?from={start_ts}&to={stop_ts}", body=mock_views())
    data = sg.get_events(start, stop, type_="views")

    assert isinstance(data, list)
    assert all(key in record for record in data for key in ("timeWindowStart", "ttrMs", "views"))


@responses.activate
def test_get_events_visitors(publication_config):
    start = datetime(2021, 10, 4)
    stop = datetime(2021, 10, 5)
    start_ts = convert_datetime_to_unix(start)
    stop_ts = convert_datetime_to_unix(stop)

    responses.add(responses.GET, "https://medium.com/foo-blog", body=mock_homepage())
    sg = StatGrabberPublication(**publication_config)
    responses.add(
        responses.GET, sg.collections_endpoint + f"/visitors?from={start_ts}&to={stop_ts}", body=mock_visitors()
    )
    data = sg.get_events(start, stop, type_="visitors")

    assert isinstance(data, list)
    assert all(key in record for record in data for key in ("timeWindowStart", "dailyUniqueVisitors"))


@responses.activate
def test_get_summary_stats(publication_config):
    responses.add(responses.GET, "https://medium.com/foo-blog", body=mock_homepage())
    sg = StatGrabberPublication(**publication_config)
    responses.add(responses.GET, f"https://medium.com/{sg.slug}/stats/stories?limit=50", body=mock_summary_stats())
    data = sg.get_summary_stats()

    assert isinstance(data, list)
    assert data[0] == mock_story_summary_stats()
