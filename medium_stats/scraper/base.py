import json
import re
import traceback
from pathlib import Path
from typing import List

import requests
from requests import Response

from medium_stats.scraper.queries import StatsPostQueries
from medium_stats.utils import convert_datetime_to_unix


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

    def get_article_ids(self, summary_stats_json: dict) -> List[str]:

        ids = [a["postId"] for a in summary_stats_json]
        self.articles = ids
        return ids

    def get_referrer_totals(self, post_id):

        post_data = {
            "variables": {"postId": post_id},
            "operationName": "StatsPostReferrersContainer",
            "query": StatsPostQueries.REFERRER_Q.value,
        }

        response = self.session.post(self.gql_endpoint, json=post_data)
        response.raise_for_status()

        return response.json()

    def get_view_read_totals(self, post_id, start, stop):

        post_data = {
            "operationName": "StatsPostChart",
            "query": StatsPostQueries.CHART_Q.value,
            "variables": {
                "postId": post_id,
                "startAt": convert_datetime_to_unix(start),
                "endAt": convert_datetime_to_unix(stop),
            },
        }
        response = self.session.post(self.gql_endpoint, json=post_data)
        response.raise_for_status()

        return response.json()

    def write_json(self, data: dict, filepath: str) -> Path:

        if not re.search(".json$", filepath):
            filepath = f"{filepath}.json"

        try:
            data = json.dumps(data, indent=2)
        except:
            traceback.print_exc()

        with open(filepath, "w") as f:
            f.write(data)

        return Path(filepath)
