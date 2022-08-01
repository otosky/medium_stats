from datetime import datetime
from typing import Optional

import typer

from medium_stats import StatGrabberPublication
from medium_stats.cli.core import START_ARG_TYPER
from medium_stats.cli.core import STOP_ARG_TYPER
from medium_stats.cli.core import _get_articles
from medium_stats.cli.core import _get_referrers
from medium_stats.cli.core import fmt_json
from medium_stats.config import publication_config
from medium_stats.utils import select_keys

publication_app = typer.Typer()


@publication_app.command(name="summary")
def get_summary(limit: int = 50):
    """Lifetime summary view of all posts by Publication."""
    sg = StatGrabberPublication(**publication_config.as_dict())
    data = sg.get_summary_stats(limit=limit)

    typer.echo(fmt_json(data))
    return data


@publication_app.command(name="events-views")
def get_view_events(start: datetime = START_ARG_TYPER, stop: datetime = STOP_ARG_TYPER):
    sg = StatGrabberPublication(**publication_config.as_dict())
    data = sg.get_events(start, stop, type_="views")

    typer.echo(fmt_json(data))
    return data


@publication_app.command(name="events-visitors")
def get_visitor_events(start: datetime = START_ARG_TYPER, stop: datetime = STOP_ARG_TYPER):
    sg = StatGrabberPublication(**publication_config.as_dict())
    data = sg.get_events(start, stop, type_="visitors")

    typer.echo(fmt_json(data))
    return data


@publication_app.command(name="articles")
def get_articles(start: datetime = START_ARG_TYPER, stop: datetime = STOP_ARG_TYPER, post_id: Optional[str] = None):
    sg = StatGrabberPublication(**publication_config.as_dict())
    if post_id:
        data = [sg.get_view_read_totals(post_id, start, stop)]
    else:
        data = _get_articles(sg, start, stop)
    typer.echo(fmt_json(data))
    return data


@publication_app.command(name="referrers")
def get_referrers():
    sg = StatGrabberPublication(**publication_config.as_dict())
    data = _get_referrers(sg)
    typer.echo(fmt_json(data))
    return data


@publication_app.command(name="get-article-ids")
def get_article_ids():
    sg = StatGrabberPublication(**publication_config.as_dict())
    articles = sg.get_summary_stats()
    data = [select_keys({"postId", "title"}, article) for article in articles]
    typer.echo(fmt_json(data))
    return data
