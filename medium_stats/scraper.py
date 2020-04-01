from datetime import datetime, timedelta
import configparser
import requests, json
import re, os
import traceback
from medium_stats.utils import ensure_date_valid
from requests.exceptions import HTTPError

DEFAULT_END = datetime.utcnow()
DEFAULT_START = DEFAULT_END - timedelta(days=30)

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

class StatGrabber:

    def __init__(self, username, sid, uid, start, stop):

        self.username = str(username)
        self.start, self.stop = map(ensure_date_valid, (start, stop))
        self.start_unix, self.stop_unix = map(StatGrabber._convert_datetime_to_unix, (start, stop))
        self.stats_url = f'https://medium.com/@{username}/stats?filter=not-response'
        self.totals_endpoint = f'https://medium.com/@{username}/stats/total/{self.start_unix}/{self.stop_unix}'
        self.sid = sid
        self.uid = uid
        self.cookies = {'sid': sid, 'uid': uid}
        self._setup_requests()
        self.now = datetime.utcnow()

    @staticmethod
    def _convert_datetime_to_unix(dt, ms=True):
        
        dt = ensure_date_valid(dt)
        dt  = int(dt.timestamp())
        
        if ms:
            dt = dt * 1000
        
        return dt

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

    def get_summary_stats(self, events=False):
        
        json_cleaner = lambda x: x.text.replace('])}while(1);</x>', '')
        json_loader = lambda x: json.loads(x)['payload']

        if events:
            response = self._fetch(self.totals_endpoint)
        else:
            response = self._fetch(self.stats_url)

        data = json_cleaner(response)
        data = json_loader(data)
        
        # reset period "start" to when user created Medium account, if init 
        # setting is prior 
        if not events:
            user_creation = data['references']['User'][self.uid]['createdAt']
            user_creation = datetime.fromtimestamp(user_creation / 1e3)
            if self.start < user_creation:
                self.start = user_creation
                self.start_unix = StatGrabber._convert_datetime_to_unix(self.start)

        return data['value']

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
            data = json.dumps(data)
        except:
            traceback.print_exc()
        
        with open(filepath, 'w') as f:
            f.write(data)

        return filepath