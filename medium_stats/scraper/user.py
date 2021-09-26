import json
from datetime import datetime
from datetime import timezone

from medium_stats.scraper.base import StatGrabberBase
from medium_stats.utils import convert_datetime_to_unix


class StatGrabberUser(StatGrabberBase):
    def __init__(self, username, sid, uid, start, stop, now=None, already_utc=False):

        self.username = str(username)
        self.slug = str(username)
        super().__init__(sid, uid, start, stop, now, already_utc)
        # TODO: find a test User with many more posts to see how to deal with pagination
        self.stats_url = f"https://medium.com/@{username}/stats?filter=not-response&limit=50"
        self.totals_endpoint = f"https://medium.com/@{username}/stats/total/{self.start_unix}/{self.stop_unix}"

    def __repr__(self):
        return f"username: {self.username} // uid: {self.uid}"

    def get_summary_stats(self, events=False):

        if events:
            response = self._fetch(self.totals_endpoint)
        else:
            response = self._fetch(self.stats_url)

        data = self._decode_json(response)

        # reset period "start" to when user created Medium account, if init
        # setting is prior
        if not events:
            user_creation = data["references"]["User"][self.uid]["createdAt"]
            user_creation = datetime.fromtimestamp(user_creation / 1e3, timezone.utc)
            if self.start < user_creation:
                self.start = user_creation
                self.start_unix = convert_datetime_to_unix(self.start)

        return data["value"]
