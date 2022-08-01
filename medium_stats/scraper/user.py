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
        self.url = f"https://medium.com/@{username}"
        self._base_url = f"{self.url}/stats"

    def __repr__(self):  # pragma: no cover
        return f"username: {self.username} // uid: {self.uid}"

    def _get_events_url(self, start_ts, stop_ts):
        return f"{self._base_url}/total/{start_ts}/{stop_ts}"

    def get_events(self, start: datetime, stop: datetime):
        start_ts, stop_ts = map(convert_datetime_to_unix, (start, stop))

        response = self._fetch(self._get_events_url(start_ts, stop_ts))

        data = self._get_json_payload(response)
        return data["value"]

    def get_summary_stats(self, limit=50, **kwargs):
        params = {"limit": limit, "filter": "not-response", **kwargs}
        response = self._fetch(self._base_url, params=params)

        data = self._get_json_payload(response)
        if data.get("paging", {}).get("next"):
            next_cursor_idx = data["paging"]["next"]["to"]
            next_page = self.get_summary_stats(limit=limit, to=next_cursor_idx)
            data["value"].extend(next_page)

        return data["value"]
