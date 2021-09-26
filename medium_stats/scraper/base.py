import json
import re
import traceback
from datetime import datetime
from datetime import timezone
from functools import partial
from pathlib import Path
from typing import List
from typing import Optional

import requests
from lxml import html
from requests import Response

from medium_stats.scraper.queries import StatsPostQueries
from medium_stats.utils import convert_datetime_to_unix
from medium_stats.utils import make_utc_explicit


class StatGrabberBase:
    def __init__(
        self,
        sid: str,
        uid: str,
        start: datetime,
        stop: datetime,
        now: Optional[bool] = None,
        already_utc: bool = False,
    ):

        for s in [start, stop]:
            if not isinstance(s, datetime):
                msg = f'argument "{s}" must be of type datetime.datetime'
                raise TypeError(msg)

        make_utc = partial(make_utc_explicit, utc_naive=already_utc)
        self.start, self.stop = map(make_utc, (start, stop))
        self.start_unix, self.stop_unix = map(convert_datetime_to_unix, (start, stop))
        self.sid = sid
        self.uid = uid
        self.cookies = {"sid": sid, "uid": uid}
        self._setup_requests()
        if not now:
            self.now = datetime.now(timezone.utc)
        else:
            if not now.tzinfo:
                raise AttributeError(f'"now" param ({now}) must be tz-aware datetime')
            self.now = make_utc_explicit(now, utc_naive=False)

    def _setup_requests(self):

        s = requests.Session()
        s.headers.update({"content-type": "application/json", "accept": "application/json"})

        cookies = requests.utils.cookiejar_from_dict(self.cookies)
        s.cookies = cookies
        self.session = s

    def _fetch(self, url) -> Response:

        response = self.session.get(url)
        response.raise_for_status()
        return response

    def _decode_json(self, response: Response) -> dict:

        # TODO add TypeError if response is not a response object
        cleaned = response.text.replace("])}while(1);</x>", "")
        return json.loads(cleaned)["payload"]

    # TODO - delete if unnecessary
    def _find_data_in_html(self, response: Response) -> dict:

        etree = html.fromstring(response)
        refs = etree.xpath('//script[contains(text(), "references")]')[0]
        refs = refs.replace('// <![CDATA[\nwindow["obvInit"](', "")
        refs = refs.replace(")\n// ]]>", "")

        return json.loads(refs)

    def get_article_ids(self, summary_stats_json: dict) -> List[str]:

        ids = [a["postId"] for a in summary_stats_json]
        self.articles = ids
        return ids

    def get_story_stats(self, post_id, type_="view_read"):

        if type_ not in ["view_read", "referrer"]:
            raise ValueError('"type" param must be either "view_read" or "referrer"')

        gql_endpoint = "https://medium.com/_/graphql"

        post_data = {"variables": {"postId": post_id}}

        if type_ == "view_read":
            post_data["operationName"] = "StatsPostChart"
            v = post_data["variables"]
            v["startAt"], v["endAt"] = self.start_unix, self.stop_unix
            post_data["query"] = StatsPostQueries.CHART_Q.value
        elif type_ == "referrer":
            post_data["operationName"] = "StatsPostReferrersContainer"
            post_data["query"] = StatsPostQueries.REFERRER_Q.value

        r = self.session.post(gql_endpoint, json=post_data)

        return r.json()

    def get_all_story_stats(self, post_ids, type_="view_read"):

        container = {"data": {"post": []}}

        for post in post_ids:
            data = self.get_story_stats(post, type_=type_)
            container["data"]["post"] += [data["data"]["post"]]

        return container

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
