"""Module that provides functionality to download albums from Pixiv URLs.

It reads a list of URLs from a file, checks against a record of already downloaded
albums to avoid duplicates, and processes the downloads accordingly.
"""

from pathlib import Path

from rich.live import Live
from rich.table import Table

from album_downloader import download_album
from helpers.config import ALREADY_DOWNLOADED, FILE
from helpers.file_utils import read_file, write_file
from helpers.general_utils import clear_terminal
from helpers.progress_utils import (
    create_log_table,
    create_progress_bar,
    create_progress_table,
)


def manage_combined_table(
    live: Live, progress_table: Table, log_messages: list[str],
) -> None:
    """Manage and updates a table by merging progress data with log messages."""
    if log_messages:
        log_table = create_log_table(log_messages)
        combined_table = Table.grid()
        combined_table.add_row(progress_table)
        combined_table.add_row(log_table)
        live.update(combined_table)


def process_urls(urls: list[str]) -> None:
    """Validate and downloads albums from a list of URLs."""
    if not Path(ALREADY_DOWNLOADED).exists():
        write_file(ALREADY_DOWNLOADED)

    already_downloaded_albums = set(read_file(ALREADY_DOWNLOADED))
    log_messages = []

    overall_progress = create_progress_bar()
    job_progress = create_progress_bar()
    progress_table = create_progress_table(overall_progress, job_progress)

    with Live(progress_table, refresh_per_second=10) as live:
        for url in urls:
            if "www.pixiv.net" in url:
                to_download = url not in already_downloaded_albums

                if to_download:
                    download_album(url, overall_progress, job_progress)
                    write_file(ALREADY_DOWNLOADED, url, mode="a")
                else:
                    log_messages.append(url)

        manage_combined_table(live, progress_table, log_messages)


def main() -> None:
    """Run the script."""
    clear_terminal()
    urls = read_file(FILE)
    process_urls(urls)
    write_file(FILE)


if __name__ == "__main__":
    main()
