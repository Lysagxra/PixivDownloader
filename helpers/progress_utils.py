"""Module that provides utility functions for tracking download progress.

It includes features for creating a progress bar, a formatted progress table for
monitoring download status, and a log table for displaying downloaded messages.
"""

from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .config import TITLE_COLOR


def create_progress_bar() -> Progress:
    """Create a progress bar for tracking download progress."""
    return Progress(
        "{task.description}",
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    )


def create_progress_table(overall_progress: Progress, job_progress: Progress) -> Table:
    """Create a formatted progress table for tracking the download."""
    progress_table = Table.grid()
    progress_table.add_row(
        Panel.fit(
            overall_progress,
            title=f"[b {TITLE_COLOR}]Overall Progress",
            # Good alternatives: "orange3", "orange4"
            border_style="bright_blue",
            padding=(1, 1),
            width=40,
        ),
        Panel.fit(
            job_progress,
            title=f"[b {TITLE_COLOR}]Album Progress",
            border_style="medium_purple",
            padding=(1, 1),
            width=40,
        ),
    )
    return progress_table


def create_log_table(log_messages: list[str]) -> Table:
    """Create a formatted log table to display downloaded messages."""
    log_row = "\n".join([f"• {message}" for message in log_messages])
    log_table = Table.grid()
    log_table.add_row(
        Panel(
            log_row,
            title=f"[b {TITLE_COLOR}]Already Downloaded",
            border_style="grey35",
            padding=(1, 1),
            width=80,
        ),
    )
    return log_table
