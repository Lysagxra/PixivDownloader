"""
This module provides functionality to download albums from Pixiv URLs. It
reads a list of URLs from a file, checks against a record of already downloaded
albums to avoid duplicates, and processes the downloads accordingly.
"""
import os
from rich.live import Live
from rich.table import Table

from album_downloader import download_album
from helpers.progress_utils import (
    create_progress_bar, create_progress_table, create_log_table
)

FILE = 'URLs.txt'
ALREADY_DOWNLOADED = 'already_downloaded.txt'
HOST_BASE_LINK = 'www.pixiv.net'

def read_file(filename):
    """
    Reads the contents of a file and returns a list of its lines.

    Args:
        filename (str): The path to the file to be read.

    Returns:
        list: A list of lines from the file, with newline characters removed.
    """
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read().splitlines()

def write_file(filename, content='', mode='w'):
    """
    Writes or appends content to a specified file.

    Args:
        filename (str): The path to the file to be written to.
        content (str, optional): The content to write to the file.
                                 Defaults to an empty string.
        mode (str, optional): The mode for file operation.
                              'w' for overwrite (default) or 'a' for append.

    Raises:
        IOError: If an error occurs while writing to the file.
    """
    with open(filename, mode, encoding='utf-8') as file:
        file.write(f"{content}\n" if mode == 'a' else content)

def manage_combined_table(live, progress_table, log_messages):
    """
    Manages and updates a combined table by merging progress data with log
    messages.

    Args:
        live (Live): An instance of the Live class used for updating the
                     display.
        progress_table (Table): A table containing the current progress data.
    """
    if log_messages:
        log_table = create_log_table(log_messages)
        combined_table = Table.grid()
        combined_table.add_row(progress_table)
        combined_table.add_row(log_table)
        live.update(combined_table)

def process_urls(urls):
    """
    Validates and downloads albums from a list of URLs.
    The function also initializes progress tracking and logging, displaying
    the status of downloads in a combined progress and log table.

    Args:
        urls (list of str): A list of URLs to process for album downloads.
    """
    if not os.path.exists(ALREADY_DOWNLOADED):
        write_file(ALREADY_DOWNLOADED)

    already_downloaded_albums = set(read_file(ALREADY_DOWNLOADED))

    overall_progress = create_progress_bar()
    job_progress = create_progress_bar()
    progress_table = create_progress_table(overall_progress, job_progress)

    log_messages = []
    with Live(progress_table, refresh_per_second=10) as live:
        for url in urls:
            if HOST_BASE_LINK in url:
                to_download = url not in already_downloaded_albums

                if to_download:
                    download_album(url, overall_progress, job_progress)
                    write_file(ALREADY_DOWNLOADED, url, mode='a')
                else:
                    log_messages.append(url)

        manage_combined_table(live, progress_table, log_messages)

def main():
    """
    Main function to execute the script.

    This function reads a list of URLs from a specified file, processes each URL
    to download albums while checking for previously downloaded entries, and
    clears the URL file upon completion.
    """
    urls = read_file(FILE)
    process_urls(urls)
    write_file(FILE)

if __name__ == '__main__':
    main()
