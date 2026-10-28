"""Command-line interface."""

from __future__ import annotations

import typer

from coauthored import __version__, guard

app = typer.Typer(no_args_is_help=True, help="Count AI-attributed commits in git history.")


@app.callback()
def _main() -> None:
    guard.check()


@app.command()
def version() -> None:
    """Print the version."""
    typer.echo(__version__)
