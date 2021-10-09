from datetime import datetime

from medium_stats.scraper.base import StatGrabberBase
from medium_stats.utils import convert_datetime_to_unix


class StatGrabberPublication(StatGrabberBase):
    def __init__(self, slug: str, sid: str, uid: str):
        super().__init__(sid, uid)

        self.url = "https://medium.com/" + slug
        homepage = self._fetch(self.url)  # TODO figure out why requests lib doesn't get full html from this url
        data = self._get_json_payload(homepage)
        self._attrs_json = data["collection"]
        self._unpack_attrs(self._attrs_json)

        self.collections_endpoint = f"https://medium.com/_/api/collections/{self.id}/stats"

    def _unpack_attrs(self, attrs_json: dict):

        self.id = attrs_json["id"]
        self.slug = attrs_json["slug"]
        self.name = attrs_json["name"]
        self.creator = attrs_json["creatorId"]
        self.description = attrs_json["description"]
        try:
            self.domain = self._attrs_json["domain"]
        except KeyError:
            self.domain = None

    def get_events(self, start: datetime, stop: datetime, type_: str):
        url = "/".join([self.collections_endpoint, type_])
        params = {"from": convert_datetime_to_unix(start), "to": convert_datetime_to_unix(stop)}

        response = self._fetch(url, params=params)
        data = self._get_json_payload(response)
        return data["value"]

    def get_summary_stats(self):

        # TODO: need to figure out how pagination works after limit exceeded
        endpoint = f"https://medium.com/{self.slug}/stats/stories?limit=50"
        response = self._fetch(endpoint)
        data = self._get_json_payload(response)

        return data["value"]

    def __repr__(self):  # pragma: no cover
        return f"{self.name} - {self.description}"
