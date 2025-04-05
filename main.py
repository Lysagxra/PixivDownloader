"""Module that provides functionality to download albums from Pixiv URLs.

It reads a list of URLs from a file, checks against a record of already downloaded
albums to avoid duplicates, and processes the downloads accordingly.
"""

from pathlib import Path

from album_downloader import download_album, initialize_managers
from helpers.config import ALREADY_DOWNLOADED, FILE
from helpers.file_utils import read_file, write_file
from helpers.general_utils import clear_terminal


def process_urls(urls: list[str]) -> None:
    """Validate and downloads albums from a list of URLs."""
    if not Path(ALREADY_DOWNLOADED).exists():
        write_file(ALREADY_DOWNLOADED)

    already_downloaded_albums = set(read_file(ALREADY_DOWNLOADED))
    live_manager = initialize_managers()

    with live_manager.live:
        for url in urls:
            if "www.pixiv.net" in url:
                to_download = url not in already_downloaded_albums

                if to_download:
                    download_album(url, live_manager)
                    write_file(ALREADY_DOWNLOADED, url, mode="a")
                else:
                    album_id = url.split("/")[-1]
                    live_manager.update_log(
                        "Skipped download",
                        f"Album {album_id} has already been downloaded.",
                    )
        live_manager.stop()


def main() -> None:
    """Run the script."""
    clear_terminal()
    urls = read_file(FILE)
    process_urls(urls)
    write_file(FILE)


if __name__ == "__main__":
    main()
