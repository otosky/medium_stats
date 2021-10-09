import os
from datetime import datetime

import lazy_object_proxy
import typer

from medium_stats import StatGrabberPublication
from medium_stats.cli.core import START_ARG_TYPER
from medium_stats.cli.core import STOP_ARG_TYPER
from medium_stats.cli.core import _get_articles
from medium_stats.cli.core import _get_referrers
from medium_stats.cli.core import fmt_json

publication_app = typer.Typer()

sg = lazy_object_proxy.Proxy(
    lambda: StatGrabberPublication(
        slug=os.environ["MEDIUM_PUBLICATION_SLUG"],
        sid=os.environ["MEDIUM_SID"],
        uid=os.environ["MEDIUM_UID"],
    )
)


@publication_app.command(name="overview")
def get_overview():
    """Lifetime summary view of all posts by Publication."""
    data = sg.get_summary_stats()

    typer.echo(fmt_json(data))


@publication_app.command(name="views")
def get_view_events(start: datetime = START_ARG_TYPER, stop: datetime = STOP_ARG_TYPER):
    data = sg.get_events(start, stop, type_="views")

    typer.echo(fmt_json(data))


@publication_app.command(name="visitors")
def get_visitor_events(start: datetime = START_ARG_TYPER, stop: datetime = STOP_ARG_TYPER):
    data = sg.get_events(start, stop, type_="visitors")

    typer.echo(fmt_json(data))


@publication_app.command(name="articles")
def get_articles(start: datetime = START_ARG_TYPER, stop: datetime = STOP_ARG_TYPER):
    data = _get_articles(sg, start, stop)
    typer.echo(fmt_json(data))


@publication_app.command(name="referrers")
def get_referrers():
    data = _get_referrers(sg)
    typer.echo(fmt_json(data))
