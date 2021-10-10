import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List
from typing import Union

import dotenv
import lazy_object_proxy
import typer

START_ARG_TYPER = typer.Argument(..., help="Date range start; %Y-%m-%d or %Y-%m-%dT%H:%M:%S", metavar="START")
STOP_ARG_TYPER = typer.Argument(..., help="Date range end (exclusive); %Y-%m-%d or %Y-%m-%dT%H:%M:%S", metavar="STOP")


@dataclass
class PublicationConfig:
    sid: str
    uid: str
    slug: str

    @staticmethod
    def from_env():
        dotenv.load_dotenv()
        return PublicationConfig(
            sid=os.environ["MEDIUM_SID"], uid=os.environ["MEDIUM_UID"], slug=os.environ["MEDIUM_PUBLICATION_SLUG"]
        )

    def as_dict(self):
        return self.__dict__


publication_config = lazy_object_proxy.Proxy(lambda: PublicationConfig.from_env())


@dataclass
class UserConfig:
    sid: str
    uid: str
    username: str

    @staticmethod
    def from_env():
        dotenv.load_dotenv()
        return UserConfig(
            sid=os.environ["MEDIUM_SID"], uid=os.environ["MEDIUM_UID"], username=os.environ["MEDIUM_USERNAME"]
        )

    def as_dict(self):
        return self.__dict__


user_config = lazy_object_proxy.Proxy(lambda: UserConfig.from_env())


def fmt_json(data: Union[List[dict], dict]):
    return json.dumps(data, indent=2, default=str)


def _get_articles(stat_grabber, start: datetime, stop: datetime):
    """Views/Reads by article."""

    all_posts = stat_grabber.get_summary_stats()
    articles = stat_grabber.get_article_ids(all_posts)
    data = [stat_grabber.get_view_read_totals(article, start, stop) for article in articles]

    return data


def _get_referrers(stat_grabber):
    """Views directed by Referrer per article."""
    all_posts = stat_grabber.get_summary_stats()
    articles = stat_grabber.get_article_ids(all_posts)
    data = [stat_grabber.get_referrer_totals(article) for article in articles]

    return data
