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
from medium_stats.cli.core import user_config

user_app = typer.Typer()

sg = lazy_object_proxy.Proxy(lambda: StatGrabberUser(**user_config.as_dict()))


@user_app.command(name="summary")
def get_summary():
    """Lifetime stats per post."""
    post_stats = sg.get_summary_stats()

    typer.echo(fmt_json(post_stats))


@user_app.command(name="events")
def get_events(start: datetime = START_ARG_TYPER, stop: datetime = STOP_ARG_TYPER):
    events = sg.get_events(start, stop)

    typer.echo(fmt_json(events))


@user_app.command(name="articles")
def get_articles(start: datetime = START_ARG_TYPER, stop: datetime = STOP_ARG_TYPER):
    data = _get_articles(sg, start, stop)
    typer.echo(fmt_json(data))


@user_app.command(name="referrers")
def get_referrers():
    data = _get_referrers(sg)
    typer.echo(fmt_json(data))
