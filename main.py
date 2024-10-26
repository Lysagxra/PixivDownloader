"""
This module provides functionality to download albums from Pixiv URLs. It
reads a list of URLs from a file, checks against a record of already downloaded
albums to avoid duplicates, and processes the downloads accordingly.

Key Functions:
- read_file: Reads the contents of a specified file and returns a list of lines.
- write_file: Writes or appends content to a specified file.
- process_urls: Validates and downloads albums from a list of URLs.
- main: The entry point of the module, orchestrating the reading, processing,
        and writing of URLs.

Files Used:
- URLs.txt: The file containing the list of URLs to process.
- already_downloaded.txt: A record of albums that have already been downloaded.

Usage:
Run this module as a standalone script to initiate the album downloading process.
"""

from album_downloader import download_album

FILE = 'URLs.txt'
ALREADY_DOWNLOADED = 'already_downloaded.txt'

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

def process_urls(urls):
    """
    Validates and downloads albums from a list of URLs.

    This function checks each URL against a list of already downloaded albums.
    If an album has already been downloaded, it skips the download. Otherwise,
    it downloads the album and appends the URL to the list of downloaded albums.

    Args:
        urls (list of str): A list of URLs to process for album downloads.
    """
    already_downloaded_albums = set(read_file(ALREADY_DOWNLOADED))

    for url in urls:
        if url in already_downloaded_albums:
            print(f"Album has been already downloaded from the URL: {url}")
            continue

        download_album(url)
        write_file(ALREADY_DOWNLOADED, url, mode='a')

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
