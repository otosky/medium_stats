from datetime import datetime, timedelta, timezone
import configparser
import requests, json
import re, os
import traceback
from medium_stats.utils import make_utc_explicit, convert_datetime_to_unix
from requests.exceptions import HTTPError
from lxml import html
from functools import partial

stats_post_chart_q = '''\
    query StatsPostChart($postId: ID!, $startAt: Long!, $endAt: Long!) {
      post(id: $postId) {
        id
        ...StatsPostChart_dailyStats
        ...StatsPostChart_dailyEarnings
        __typename
      }
    }

    fragment StatsPostChart_dailyStats on Post {
      dailyStats(startAt: $startAt, endAt: $endAt) {
        periodStartedAt
        views
        internalReferrerViews
        memberTtr
        __typename
      }
      __typename
    }

    fragment StatsPostChart_dailyEarnings on Post {
      earnings {
        dailyEarnings(startAt: $startAt, endAt: $endAt) {
          periodEndedAt
          periodStartedAt
          amount
          __typename
        }
        lastCommittedPeriodStartedAt
        __typename
      }
      __typename
    }'''

stats_post_ref_q = '''\
    query StatsPostReferrersContainer($postId: ID!) {
        post(id: $postId) {
            id
            ...StatsPostReferrersExternalRow_post
            referrers {
              ...StatsPostReferrersContainer_referrers
              __typename
            }
            totalStats {
              ...StatsPostReferrersAll_totalStats
              __typename
            }
            __typename
        }
    }

    fragment StatsPostReferrersExternalRow_post on Post {
      title
      __typename
    }

    fragment StatsPostReferrersContainer_referrers on Referrer {
      postId
      sourceIdentifier
      totalCount
      type
      internal {
        postId
        collectionId
        profileId
        type
        __typename
      }
      search {
        domain
        keywords
        __typename
      }
      site {
        href
        title
        __typename
      }
      platform
      __typename
    }

    fragment StatsPostReferrersAll_totalStats on SummaryPostStat {
      views
      __typename
    }
'''

class StatGrabberBase:

    def __init__(self, sid, uid, start, stop, now=None, already_utc=False):

        for s in [start, stop]:
            if not isinstance(s, datetime):
                msg = f'argument "{s}" must be of type datetime.datetime'
                raise TypeError(msg)

        make_utc = partial(make_utc_explicit, utc_naive=already_utc)
        self.start, self.stop = map(make_utc, (start, stop))
        self.start_unix, self.stop_unix = map(convert_datetime_to_unix, (start, stop))
        self.sid = sid
        self.uid = uid
        self.cookies = {'sid': sid, 'uid': uid}
        self._setup_requests()
        if not now:
            self.now = datetime.now(timezone.utc)
        else:
            if not now.tzinfo:
                raise AttributeError(f'"now" param ({now}) must be tz-aware datetime')
            self.now = make_utc_explicit(now, utc_naive=False)

    def _setup_requests(self):
        
        s = requests.Session()
        s.headers.update({'content-type': 'application/json', 'accept': 'application/json'})
        
        cookies = requests.utils.cookiejar_from_dict(self.cookies)
        s.cookies = cookies
        self.session = s

    def _fetch(self, url):

        response = self.session.get(url)
        response.raise_for_status()
        return response

    def _decode_json(self, response):

        # TODO add TypeError if response is not a response object
        cleaned = response.text.replace('])}while(1);</x>', '')
        return json.loads(cleaned)['payload']

    # TODO - delete if unnecessary
    def _find_data_in_html(self, response):

        etree = html.fromstring(response)
        refs = etree.xpath('//script[contains(text(), "references")]')[0]
        refs = refs.replace('// <![CDATA[\nwindow["obvInit"](', '')
        refs = refs.replace(')\n// ]]>', '')
        
        return json.loads(refs)

    def get_article_ids(self, summary_stats_json):

        ids = [a['postId'] for a in summary_stats_json]
        self.articles = ids
        return ids

    def get_story_stats(self, post_id, type_='view_read'):

        if type_ not in ['view_read', 'referrer']:
            raise ValueError('"type" param must be either "view_read" or "referrer"')
        
        gql_endpoint = 'https://medium.com/_/graphql'

        post_data = {
            "variables": {
                "postId": post_id
            }
        }

        if type_ == 'view_read':
            post_data['operationName'] = 'StatsPostChart'
            v = post_data['variables']
            v['startAt'], v['endAt'] = self.start_unix, self.stop_unix
            post_data['query'] = stats_post_chart_q
        elif type_ == 'referrer':
            post_data['operationName'] = 'StatsPostReferrersContainer'
            post_data['query'] = stats_post_ref_q

        r = self.session.post(gql_endpoint, json=post_data)
        
        return r.json()
    
    def get_all_story_stats(self, post_ids, type_='view_read'):

        container = {'data': {'post': []}}

        for post in post_ids:
            data = self.get_story_stats(post, type_=type_)
            container['data']['post'] += [data['data']['post']]
        
        return container

    def write_json(self, data, filepath):

        if not re.search(".json$", filepath):
            filepath = f"{filepath}.json"

        try:
            data = json.dumps(data, indent=2)
        except:
            traceback.print_exc()
        
        with open(filepath, 'w') as f:
            f.write(data)

        return filepath

class StatGrabberUser(StatGrabberBase):

    def __init__(self, username, sid, uid, start, stop, now=None, already_utc=False):
      
      self.username = str(username)
      self.slug = str(username)
      super().__init__(sid, uid, start, stop, now, already_utc)
      # TODO: find a test User with many more posts to see how to deal with pagination
      self.stats_url = f'https://medium.com/@{username}/stats?filter=not-response&limit=50'
      self.totals_endpoint = f'https://medium.com/@{username}/stats/total/{self.start_unix}/{self.stop_unix}'
    
    def __repr__(self):
        return f'username: {self.username} // uid: {self.uid}'

    def get_summary_stats(self, events=False):

        if events:
            response = self._fetch(self.totals_endpoint)
        else:
            response = self._fetch(self.stats_url)

        data = self._decode_json(response)
        
        # reset period "start" to when user created Medium account, if init 
        # setting is prior 
        if not events:
            user_creation = data['references']['User'][self.uid]['createdAt']
            user_creation = datetime.fromtimestamp(user_creation / 1e3, timezone.utc)
            if self.start < user_creation:
                self.start = user_creation
                self.start_unix = convert_datetime_to_unix(self.start)

        return data['value']

class StatGrabberPublication(StatGrabberBase):

    def __init__(self, slug, sid, uid, start, stop, now=None, already_utc=False):
        
        url = 'https://medium.com/' + slug
        self.url = url
        super().__init__(sid, uid, start, stop, now, already_utc)
        homepage = self._fetch(self.url)
        # TODO figure out why requests lib doesn't get full html from this url
        data = self._decode_json(homepage)
        self.attrs_json = data['collection']
        self._unpack_attrs(self.attrs_json)
        
        collections_endpoint = f'https://medium.com/_/api/collections/{self.id}/stats/'
        timeframe = f'?from={self.start_unix}&to={self.stop_unix}'
        create_endpoint = lambda x: collections_endpoint + x + timeframe
        self.views_endpoint = create_endpoint('views')
        self.visitors_endpoint = create_endpoint('visitors')

    #TODO - create a helper classmethod that takes in a URL and extracts slug

    def _unpack_attrs(self, attrs_json):

        self.id = self.attrs_json['id']
        self.slug = self.attrs_json['slug']
        self.name = self.attrs_json['name']
        self.creator = self.attrs_json['creatorId']
        self.description = self.attrs_json['description']
        try:
            self.domain = self.attrs_json['domain']
        except:
            self.domain = None
        creation = self.attrs_json['metadata']['activeAt']
        creation = datetime.fromtimestamp(creation / 1e3, timezone.utc)
        # timestamps come in hourly buckets, so this is a safety mechanism
        creation = creation - timedelta(hours=2) 
        if self.start < creation:
            self.start = creation
            self.start_unix = convert_datetime_to_unix(self.start)

    def __repr__(self):
        return f'{self.name} - {self.description}'

    def get_events(self, type_='views'):
      
        if type_ == 'views':
            response = self._fetch(self.views_endpoint)
        elif type_ == 'visitors':
            response = self._fetch(self.visitors_endpoint)
        else:
            raise ValueError('"type_" param must be either "views" or "visitors"')
        
        data = self._decode_json(response)

        return data['value']

    def get_all_story_overview(self):
        
        # TODO: need to figure out how pagination works after limit exceeded
        endpoint = f'https://medium.com/{self.slug}/stats/stories?limit=50'
        response = self._fetch(endpoint)
        data = self._decode_json(response)
        
        return data['value']