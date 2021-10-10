import json
from typing import List

import requests
from requests import Response

from medium_stats.scraper.queries import get_chart_query
from medium_stats.scraper.queries import get_referrer_query


class StatGrabberBase:
    def __init__(
        self,
        sid: str,
        uid: str,
    ):

        self.sid = sid
        self.uid = uid
        self.cookies = {"sid": sid, "uid": uid}
        self.gql_endpoint = "https://medium.com/_/graphql"
        self._setup_requests()
        self.articles = []

    def _setup_requests(self):

        s = requests.Session()
        s.headers.update({"content-type": "application/json", "accept": "application/json"})

        cookies = requests.utils.cookiejar_from_dict(self.cookies)
        s.cookies = cookies
        self.session = s

    def _fetch(self, url, params=None) -> Response:

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response

    @staticmethod
    def _get_json_payload(response: Response) -> dict:

        cleaned = response.text.replace("])}while(1);</x>", "")
        return json.loads(cleaned)["payload"]

    def get_article_ids(self, summary_stats_json: List[dict]) -> List[str]:

        ids = [a["postId"] for a in summary_stats_json]
        self.articles = ids
        return ids

    def get_referrer_totals(self, post_id):

        gql_query = get_referrer_query(post_id)
        response = self.session.post(self.gql_endpoint, json=gql_query)
        response.raise_for_status()

        return response.json()["data"]["post"]

    def get_all_referrer_totals(self, post_ids):
        return [self.get_referrer_totals(post_id) for post_id in post_ids]

    def get_view_read_totals(self, post_id, start, stop):

        gql_query = get_chart_query(post_id, start, stop)
        response = self.session.post(self.gql_endpoint, json=gql_query)
        response.raise_for_status()

        return response.json()["data"]["post"]

    def get_all_view_read_totals(self, post_ids, start, stop):
        return [self.get_view_read_totals(post_id, start, stop) for post_id in post_ids]

    # # TODO fixme
    # @staticmethod
    # def write_json(data: dict, filepath: str) -> Path:
    #
    #     if not re.search(".json$", filepath):
    #         filepath = f"{filepath}.json"
    #
    #     try:
    #         data = json.dumps(data, indent=2)
    #     except:
    #         traceback.print_exc()
    #
    #     with open(filepath, "w") as f:
    #         f.write(data)
    #
    #     return Path(filepath)
