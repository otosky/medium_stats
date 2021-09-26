from enum import Enum


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
