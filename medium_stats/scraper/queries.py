from enum import Enum

from medium_stats.utils import convert_datetime_to_unix


class StatsPostQueries(Enum):
    CHART_Q = """\
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
        }"""

    REFERRER_Q = """\
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
    """


def get_chart_query(post_id, start, stop):
    post_query = {
        "operationName": "StatsPostChart",
        "query": StatsPostQueries.CHART_Q.value,
        "variables": {
            "postId": post_id,
            "startAt": convert_datetime_to_unix(start),
            "endAt": convert_datetime_to_unix(stop),
        },
    }
    return post_query


def get_referrer_query(post_id):
    post_query = {
        "operationName": "StatsPostReferrersContainer",
        "query": StatsPostQueries.REFERRER_Q.value,
        "variables": {"postId": post_id},
    }
    return post_query
