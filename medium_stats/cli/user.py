import os
from datetime import datetime

import lazy_object_proxy
import typer

from medium_stats import StatGrabberUser
from medium_stats.cli.core import START_ARG_TYPER
from medium_stats.cli.core import STOP_ARG_TYPER
from medium_stats.cli.core import _get_articles
from medium_stats.cli.core import _get_referrers
from medium_stats.cli.core import fmt_json
from medium_stats.config import user_config
from medium_stats.utils import select_keys

user_app = typer.Typer()


@user_app.command(name="summary")
def get_summary(limit: int = 50):
    """Lifetime stats per post."""
    sg = StatGrabberUser(**user_config.as_dict())
    post_stats = sg.get_summary_stats(limit=limit)

    typer.echo(fmt_json(post_stats))


@user_app.command(name="events")
def get_events(start: datetime = START_ARG_TYPER, stop: datetime = STOP_ARG_TYPER):
    sg = StatGrabberUser(**user_config.as_dict())
    events = sg.get_events(start, stop)

    typer.echo(fmt_json(events))


@user_app.command(name="articles")
def get_articles(start: datetime = START_ARG_TYPER, stop: datetime = STOP_ARG_TYPER):
    sg = StatGrabberUser(**user_config.as_dict())
    data = _get_articles(sg, start, stop)
    typer.echo(fmt_json(data))


@user_app.command(name="referrers")
def get_referrers():
    sg = StatGrabberUser(**user_config.as_dict())
    data = _get_referrers(sg)
    typer.echo(fmt_json(data))


@user_app.command(name="get-article-ids")
def get_article_ids():
    sg = StatGrabberUser(**user_config.as_dict())
    articles = sg.get_summary_stats()
    data = [select_keys({"postId", "title"}, article) for article in articles]
    typer.echo(fmt_json(data))
