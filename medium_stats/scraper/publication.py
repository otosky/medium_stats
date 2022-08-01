from datetime import datetime

from medium_stats.scraper.base import StatGrabberBase
from medium_stats.utils import convert_datetime_to_unix


class StatGrabberPublication(StatGrabberBase):
    def __init__(self, slug: str, sid: str, uid: str):
        super().__init__(sid, uid)

        self.url = "https://medium.com/" + slug

        data = self._get_homepage_data()
        self._attrs_json = data["collection"]
        self._unpack_attrs(self._attrs_json)

        self.collections_endpoint = f"https://medium.com/_/api/collections/{self.id}/stats"

    def _get_homepage_data(self):
        homepage = self._fetch(self.url)  # TODO figure out why requests lib doesn't get full html from this url
        return self._get_json_payload(homepage)

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

    def get_summary_stats(self, limit=50, **kwargs):
        params = {"limit": limit, **kwargs}
        url = f"{self.url}/stats/stories"
        response = self._fetch(url, params=params)

        data = self._get_json_payload(response)
        if data.get("paging", {}).get("next"):
            next_cursor_idx = data["paging"]["next"]["to"]
            next_page = self.get_summary_stats(limit=limit, to=next_cursor_idx)
            data["value"].extend(next_page)

        return data["value"]

    def __repr__(self):  # pragma: no cover
        return f"{self.name} - {self.description}"
