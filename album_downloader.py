"""Module that provides functionality to download artwork albums from Pixiv.

It handles various artwork types, including images and GIFs, by fetching metadata,
constructing appropriate URLs, and downloading content while displaying download
progress.
"""

import json
import logging
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from rich.live import Live
from rich.progress import Progress

from helpers.config import (
    DOWNLOAD_FOLDER,
    GIF_ILLUST_TYPE,
    HTTP_STATUS_OK,
    IMAGE_ILLUST_TYPES,
    MAX_WORKERS,
    TASK_COLOR,
)
from helpers.download_utils import (
    manage_running_tasks,
    save_gif_from_response,
    save_image_from_response,
)
from helpers.general_utils import clear_terminal
from helpers.progress_utils import create_progress_bar, create_progress_table


class ArtworkDownloader:
    """Class used to download artwork from a given URL."""

    def __init__(
        self,
        url: str,
        download_path: str,
        overall_progress: Progress,
        job_progress: Progress,
    ) -> None:
        """Initialize the ArtworkDownloader."""
        self.url = url
        self.download_path = download_path
        self.overall_progress = overall_progress
        self.job_progress = job_progress
        self.artwork = None
        self.artwork_id = None
        self.data = None

    def process_illust_data(self, illust_data: dict) -> bool:
        """Process illustration data to extract and prepare artwork information."""
        user_illusts = illust_data["userIllusts"]

        if "userIllusts" in illust_data and self.artwork_id in user_illusts:
            self.artwork = illust_data["userIllusts"][self.artwork_id]
            self.download_path = self.create_download_directory()
            self.handle_artwork_type()
            return True

        return False

    def process_artwork_from_data(self) -> None:
        """Process artwork data from the illustration dataset."""
        data_items = self.data["illust"].items()
        for _, illust_data in data_items:
            self.process_illust_data(illust_data)

    def download(self) -> None:
        """Download artwork by fetching its metadata.

        This method parses the metadata, identifies the artwork, and triggers
        downloading of either images or GIFs based on theartwork type.
        """
        (self.artwork_id, self.data) = fetch_artwork_data(self.url)

        if "illust" in self.data:
            self.process_artwork_from_data()

    def create_download_directory(self) -> str:
        """Create a directory to store the downloaded artwork."""
        page_count = self.artwork.get("pageCount")

        if page_count > 1:
            download_path = Path(DOWNLOAD_FOLDER) / self.artwork_id
        else:
            download_path = self.download_path

        Path(download_path).mkdir(parents=True, exist_ok=True)
        return download_path

    def handle_artwork_type(self) -> None:
        """Handle different types of artwork by checking if it is an image or GIF."""
        illust_type = self.artwork.get("illustType")
        if illust_type in IMAGE_ILLUST_TYPES:
            self.process_artwork_images()

        elif illust_type == GIF_ILLUST_TYPE:
            self.process_artwork_gifs()

    def process_artwork_images(self, max_workers: int = MAX_WORKERS) -> None:
        """Download individual images from the artwork."""
        images = self.artwork.get("pageCount", 1)
        futures = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            overall_task = self.overall_progress.add_task(
                f"[{TASK_COLOR}]{self.artwork_id}",
                total=images,
                visible=True,
            )

            for image in range(images):
                task = self.job_progress.add_task(
                    f"[{TASK_COLOR}]Picture {image + 1}/{images}",
                    total=100,
                    visible=False,
                )

                image_info = (self.artwork, image)
                task_info = (
                    self.job_progress,
                    self.overall_progress,
                    task,
                    overall_task,
                )

                future = executor.submit(
                    save_image_from_response,
                    image_info,
                    self.download_path,
                    task_info,
                )
                futures[future] = task
                manage_running_tasks(futures, self.job_progress)

    def process_artwork_gifs(self) -> None:
        """Download the GIF of the artwork."""
        overall_task = self.overall_progress.add_task(
            f"[{TASK_COLOR}]{self.artwork_id}",
            total=1,
            visible=True,
        )
        save_gif_from_response(
            self.artwork,
            self.download_path,
            (self.job_progress, self.overall_progress, 0, overall_task),
        )


def fetch_artwork_data(url: str) -> tuple:
    """Fetch the artwork data by making an HTTP request to the provided URL."""
    if not isinstance(url, str):
        logging.exception("The provided URL is not a string")
        sys.exit(1)

    headers = {"Referer": "http://www.pixiv.net/"}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != HTTP_STATUS_OK:
        response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    meta_content = soup.find("meta", {"id": "meta-preload-data"}).get("content")
    data = json.loads(meta_content)

    match = re.search(r"artworks/(\d+)", url)
    if not match:
        logging.exception("No artwork ID found")
        sys.exit(1)

    artwork_id = match.group(1)
    return artwork_id, data


def download_album(
    url: str,
    overall_progress: Progress,
    job_progress: Progress,
) -> None:
    """Download an album from the provided URL."""
    artwork_downloader = ArtworkDownloader(
        url=url,
        download_path=DOWNLOAD_FOLDER,
        overall_progress=overall_progress,
        job_progress=job_progress,
    )
    artwork_downloader.download()


def main() -> None:
    """Run the application."""
    if len(sys.argv) != 2:
        script_name = Path(__file__).name
        message = f"Usage: python3 {script_name} <album_url>"
        logging.error(message)
        sys.exit(1)

    clear_terminal()
    url = sys.argv[1]

    overall_progress = create_progress_bar()
    job_progress = create_progress_bar()
    progress_table = create_progress_table(overall_progress, job_progress)

    with Live(progress_table, refresh_per_second=10):
        download_album(url, overall_progress, job_progress)


if __name__ == "__main__":
    main()
