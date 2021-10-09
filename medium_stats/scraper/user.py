import json
from datetime import datetime
from datetime import timezone

from medium_stats.scraper.base import StatGrabberBase
from medium_stats.utils import convert_datetime_to_unix


class StatGrabberUser(StatGrabberBase):
    def __init__(self, username: str, sid: str, uid: str):
        super().__init__(sid, uid)
        self.username = str(username)

    def __repr__(self):
        return f"username: {self.username} // uid: {self.uid}"

    def get_events(self, start: datetime, stop: datetime):
        url_prefix = f"https://medium.com/@{self.username}/stats/total"
        start_ts, stop_ts = map(convert_datetime_to_unix, (start, stop))
        url = f"{url_prefix}/{start_ts}/{stop_ts}"

        response = self._fetch(url)

        data = self._get_json_payload(response)
        return data["value"]

    def get_summary_stats(self):
        url = f"https://medium.com/@{self.username}/stats?filter=not-response&limit=50"
        response = self._fetch(url)

        data = self._get_json_payload(response)
        return data["value"]
