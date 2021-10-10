import json
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from medium_stats.scraper.base import StatGrabberBase
from medium_stats.utils import convert_datetime_to_unix


class StatGrabberUser(StatGrabberBase):
    def __init__(self, username: str, sid: str, uid: str):
        super().__init__(sid, uid)
        self.username = str(username)
        self._summary_stats_url = f"https://medium.com/@{username}/stats?filter=not-response&limit=50"

    def __repr__(self):  # pragma: no cover
        return f"username: {self.username} // uid: {self.uid}"

    def _get_events_url(self, start_ts, stop_ts):
        return f"https://medium.com/@{self.username}/stats/total/{start_ts}/{stop_ts}"

    def get_events(self, start: datetime, stop: datetime):
        start_ts, stop_ts = map(convert_datetime_to_unix, (start, stop))

        response = self._fetch(self._get_events_url(start_ts, stop_ts))

        data = self._get_json_payload(response)
        return data["value"]

    def get_summary_stats(self):
        response = self._fetch(self._summary_stats_url)

        data = self._get_json_payload(response)
        return data["value"]
