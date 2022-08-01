# Medium Stats Scraper

[![CircleCI](https://circleci.com/gh/otosky/medium_stats.svg?style=shield)](https://circleci.com/gh/otosky/medium_stats)
[![codecov](https://codecov.io/gh/otosky/medium_stats/branch/master/graph/badge.svg?token=BUSIS9UAAG)](https://codecov.io/gh/otosky/medium_stats)

A command-line tool and Python lib to fetch your Medium profile/publication statistics.

*Executes the same API and Graphql requests as the Medium front-end does, providing you with the raw data that Medium
uses to render it's stats tables & charts.*

## Install

```bash
$ pip install medium-stats
```

## Setup

To make authenticated requests to Medium for your stats, you'll need need **two** cookies from a signed-in Medium
session - `sid` and `uid`.

*If you want to manually find and store your cookies:*

- Sign in to Medium
- Get to your browser's developer tools and find the tab that holds cookies:
    - *Application* for Chrome
    - *Storage* for Firefox
- Scroll through the cookies for medium.com until you find `sid` and `uid`

![cookie_howto](https://user-images.githubusercontent.com/42260747/136667306-0fb9cc54-301d-4712-a4a6-1b063ad9fc83.gif)

To save these to a `.env` file:

```bash
cat > .env << EOF
MEDIUM_SID=<sid_value>
MEDIUM_UID=<uid_value>
MEDIUM_USERNAME=<your_medium_username>
EOF
```

Note: if grabbing statistics for a publication add `MEDIUM_PUBLICATION_SLUG=<slug-value>` to the above heredoc.

The "slug" parameter is typically your publication's name in lower-case, with spaces delimited by dashes, and is the
portion of your page's URL after "medium.com/"

For example, the slug is `test-publication` if the URL is https://medium.com/test-publication and name is "Test Publication"

---

## Usage

### Python

#### For a User:

```python
from datetime import datetime
from medium_stats import StatGrabberUser
from medium_stats import UserConfig

# get lifetime stats & metadata for all articles
config = UserConfig(sid="sid", uid="uid", username="username")
me = StatGrabberUser(**config.as_dict())
summary = me.get_summary_stats()

# get total views and time-to-read over all posts in hourly buckets
start = datetime(year=2020, month=1, day=1)
stop = datetime(year=2020, month=4, day=1)  # note: start/stop params in all requests will be set as UTC, 

hourly_views_and_reads = me.get_events(start, stop)
```

#### Per article:

```python
article_ids = me.get_article_ids(summary)

# get daily views, time-to-read, and earnings stats per article
article_daily_stats = me.get_view_read_totals(article_ids[0], start, stop)
# get those stats for all articles
all_article_daily_stats = me.get_all_view_read_totals(article_ids, start, stop)

# get lifetime referrer stats per article
referrer_stats = me.get_referrer_totals(article_ids[0])
# get those stats for all articles
all_article_referrer_stats = me.get_all_referrer_totals(article_ids)
```

#### For a publication

```python
from medium_stats import StatGrabberPublication
from medium_stats import PublicationConfig

# first argument should be your publication slug, i.e. what follows the URL after "medium.com/"
config = PublicationConfig(sid="sid", uid="uid", slug="my-publication")
pub = StatGrabberPublication(**config.as_dict())
summary = pub.get_summary_stats()

# get total views and time-to-read over all posts in hourly buckets
views = pub.get_events(start, stop, type_='views')
visitors = pub.get_events(start, stop, type_='visitors')
```

#### Per article:

```python
# get individual article statistics
article_ids = pub.get_article_ids(story_stats)

# get daily views, time-to-read, and earnings stats per article
article_daily_stats = pub.get_view_read_totals(article_ids[0], start, stop)
# get those stats for all articles
all_article_daily_stats = pub.get_all_view_read_totals(article_ids, start, stop)

# get lifetime referrer stats per article
referrer_stats = pub.get_referrer_totals(article_ids[0])
# get those stats for all articles
all_article_referrer_stats = pub.get_all_referrer_totals(article_ids)
```

### CLI

*Make sure that you've set your environment variables in your terminal from the #setup step above.*

The `medium-stats` CLI has two main commands `scrape-user` and `scrape-publication`, each of which share similar
subcommands:

```bash
# get lifetime stats & metadata for all articles
medium-stats scrape_user summary
medium-stats scrape_publication summary

# get lifetime referrer stats per article
medium-stats scrape_user referrer
medium-stats scrape_publication referrer
```

The following commands take date range arguments in the format YYYY-MM-DD.
`STOP` dates are exclusive, i.e. up-until-but-not-including.

```bash
# get daily views, time-to-read, and earnings stats per article
medium-stats scrape_user articles START STOP
medium-stats scrape_publication articles START STOP

# get total views and time-to-read over all posts in hourly buckets
# NOTE: result is sparse, so any buckets with 0 ttrMs & 0 views are omitted
medium-stats scrape_user views START STOP # user stats are slightly different -> they include claps & upvotes but not ttr
medium-stats scrape_publication views START STOP

# get "avg number of unique daily visitors who have visited your publication"
# ONLY AVAILABLE FOR PUBLICATIONS
medium-stats scrape_publication visitors START STOP
```

The CLI is built using [typer](https://typer.tiangolo.com/) and every command includes a `--help` flag if you need to
see the usage documentation.

---

## Example Data

### Summary Stats

```
[   
  {   
    'claps': 3,
    'collectionId': '',
    'createdAt': 1570229100438,
    'creatorId': 'UID',
    'firstPublishedAt': 1583526956495,
    'friendsLinkViews': 46,
    'internalReferrerViews': 17,
    'isSeries': False,
    'postId': 'ARTICLE_ID',
    'previewImage': {   'id': 'longstring.png',
                        'isFeatured': True,
                        'originalHeight': 311,
                        'originalWidth': 627},
    'readingTime': 7,
    'reads': 67,
    'slug': 'this-will-be-a-title',
    'syndicatedViews': 0,
    'title': 'This Will Be A Title',
    'type': 'PostStat',
    'updateNotificationSubscribers': 0,
    'upvotes': 3,
    'views': 394,
    'visibility': 0
  },
      ...
]
```

### User Events

```
[
  { 
    'userId': 'UID',
    'flaggedSpam': 0,
    'timestampMs': 1585695600000,
    'upvotes': 0,
    'reads': 0,
    'views': 1
    'claps': 0,
    'updateNotificationSubscribers': 0
  },
        ...
]
```

### Publication Events

```
[
  {
    "timeWindowStart": 1633395600000,
    "ttrMs": 93000,
    "views": 10
  },
  {
    "timeWindowStart": 1633399200000,
    "ttrMs": 640000,
    "views": 20
  },
  {
    "timeWindowStart": 1633402800000,
    "ttrMs": 612302,
    "views": 31
  }
]
```

### Article Daily Stats

```
 [{
  '__typename': 'Post',
  'dailyStats': [
    {'__typename': 'DailyPostStat',
     'internalReferrerViews': 1,
     'memberTtr': 119,
     'periodStartedAt': 1583452800000,
     'views': 8},
    ...
    {'__typename': 'DailyPostStat',
     'internalReferrerViews': 5,
     'memberTtr': 375,
     'periodStartedAt': 1583539200000,
     'views': 40}],
  'earnings': {
    '__typename': 'PostEarnings',
    'dailyEarnings': [],
    'lastCommittedPeriodStartedAt': 1585526400000},
  'id': 'ARTICLE_ID'},
  ...
]}
```

### Article Referrers

```
[
  {
    '__typename': 'Post',
    'id': 'POST_ID',
    'title': 'TITLE_HERE',
    'referrers': [
      {
        '__typename': 'Referrer',
        'internal': None,
        'platform': None,
        'postId': 'POST_ID',
        'search': None,
        'site': None,
        'sourceIdentifier': 'direct',
        'totalCount': 222,
        'type': 'DIRECT'
      },
           ...
      {
        '__typename': 'Referrer',
        'internal': None,
        'platform': None,
        'postId': 'POST_ID',
        'search': None,
        'site': {
          '__typename': 'SiteReferrer',
          'href': 'https://www.inoreader.com/',
          'title': None
          },
        'sourceIdentifier': 'inoreader.com',
        'totalCount': 1,
        'type': 'SITE'
      }
    ],
  'totalStats': {
    '__typename': 'SummaryPostStat',
    'views': 395
    }
  },
  ...
]
```
