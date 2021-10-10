import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List
from typing import Union

import typer

START_ARG_TYPER = typer.Argument(..., help="Date range start; %Y-%m-%d or %Y-%m-%dT%H:%M:%S", metavar="START")
STOP_ARG_TYPER = typer.Argument(..., help="Date range end (exclusive); %Y-%m-%d or %Y-%m-%dT%H:%M:%S", metavar="STOP")


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
