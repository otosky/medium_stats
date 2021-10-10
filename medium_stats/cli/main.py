import typer

from medium_stats.cli.publication import publication_app
from medium_stats.cli.user import user_app

app = typer.Typer()

app.add_typer(user_app, name="scrape_user")
app.add_typer(publication_app, name="scrape_publication")


if __name__ == "__main__":  # pragma: no cover
    app()
