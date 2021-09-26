import json
from datetime import datetime

from medium_stats.scraper.base import StatGrabberBase


class StatGrabberPublication(StatGrabberBase):
    def __init__(self, slug: str, sid: str, uid: str, start: datetime, stop: datetime, now=None, already_utc=False):

        url = "https://medium.com/" + slug
        self.url = url
        super().__init__(sid, uid, start, stop, now, already_utc)
        homepage = self._fetch(self.url)
        # TODO figure out why requests lib doesn't get full html from this url
        data = self._decode_json(homepage)
        self.attrs_json = data["collection"]
        self._unpack_attrs(self.attrs_json)

        collections_endpoint = f"https://medium.com/_/api/collections/{self.id}/stats/"
        timeframe = f"?from={self.start_unix}&to={self.stop_unix}"
        create_endpoint = lambda x: collections_endpoint + x + timeframe
        self.views_endpoint = create_endpoint("views")
        self.visitors_endpoint = create_endpoint("visitors")

    # TODO - create a helper classmethod that takes in a URL and extracts slug

    def _unpack_attrs(self, attrs_json):

        self.id = self.attrs_json["id"]
        self.slug = self.attrs_json["slug"]
        self.name = self.attrs_json["name"]
        self.creator = self.attrs_json["creatorId"]
        self.description = self.attrs_json["description"]
        try:
            self.domain = self.attrs_json["domain"]
        except:
            self.domain = None

    def __repr__(self):
        return f"{self.name} - {self.description}"

    def get_events(self, type_: str = "views") -> dict:

        if type_ == "views":
            response = self._fetch(self.views_endpoint)
        elif type_ == "visitors":
            response = self._fetch(self.visitors_endpoint)
        else:
            raise ValueError('"type_" param must be either "views" or "visitors"')

        data = self._decode_json(response)

        return data["value"]

    def get_all_story_overview(self):

        # TODO: need to figure out how pagination works after limit exceeded
        endpoint = f"https://medium.com/{self.slug}/stats/stories?limit=50"
        response = self._fetch(endpoint)
        data = self._decode_json(response)

        return data["value"]
