def mock_article_daily_view_reads():
    return {
        "__typename": "Post",
        "dailyStats": [
            {
                "__typename": "DailyPostStat",
                "internalReferrerViews": 6,
                "memberTtr": 170,
                "periodStartedAt": 1633392000000,
                "views": 30,
            },
        ],
        "earnings": {
            "__typename": "PostEarnings",
            "dailyEarnings": [],
            "lastCommittedPeriodStartedAt": 1633651200000,
        },
        "id": "id-string",
    }


def mock_referrer_totals():
    return {
        "__typename": "Post",
        "id": "id-string",
        "referrers": [
            {
                "__typename": "Referrer",
                "internal": None,
                "platform": "TWITTER",
                "postId": "id-string",
                "search": None,
                "site": None,
                "sourceIdentifier": "twitter.com",
                "totalCount": 50,
                "type": "PLATFORM",
            },
            {
                "__typename": "Referrer",
                "internal": None,
                "platform": None,
                "postId": "id-string",
                "search": None,
                "site": None,
                "sourceIdentifier": "direct",
                "totalCount": 11,
                "type": "DIRECT",
            },
            {
                "__typename": "Referrer",
                "internal": {
                    "__typename": "InternalReferrer",
                    "collectionId": None,
                    "postId": None,
                    "profileId": None,
                    "type": "HOMEPAGE",
                },
                "platform": None,
                "postId": "id-string",
                "search": None,
                "site": None,
                "sourceIdentifier": "domain.com",
                "totalCount": 8,
                "type": "INTERNAL",
            },
        ],
        "title": "In Defense of the Untidy Data Table",
        "totalStats": {"__typename": "SummaryPostStat", "views": 100},
    }


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


def mock_events__views():
    return [
        {"timeWindowStart": 1633320000000, "ttrMs": 136008, "views": 1},
        {"timeWindowStart": 1633323600000, "ttrMs": 232381, "views": 3},
        {"timeWindowStart": 1633327200000, "ttrMs": 1001836, "views": 10},
    ]


def mock_events__visitors():
    # I'm not sure I understand this metric - how is it dailyUnique if each bucket is hourly?
    return [
        {"timeWindowStart": 1633320000000, "dailyUniqueVisitors": 83},
        {"timeWindowStart": 1633323600000, "dailyUniqueVisitors": 81},
        {"timeWindowStart": 1633327200000, "dailyUniqueVisitors": 83},
    ]


def mock_story_summary_stats():
    return [
        {
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
    ]
