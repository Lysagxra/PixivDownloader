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

from helpers.config import (
    DOWNLOAD_FOLDER,
    GIF_ILLUST_TYPE,
    HEADERS,
    HTTP_STATUS_OK,
    IMAGE_ILLUST_TYPES,
    MAX_WORKERS,
)
from helpers.download_utils import (
    manage_running_tasks,
    save_gif_from_response,
    save_image_from_response,
)
from helpers.general_utils import clear_terminal
from helpers.managers.live_manager import LiveManager
from helpers.managers.log_manager import LoggerTable
from helpers.managers.progress_manager import ProgressManager


class ArtworkDownloader:
    """Class used to download artwork from a given URL."""

    def __init__(
        self,
        url: str,
        download_path: str,
        live_manager: LiveManager,
    ) -> None:
        """Initialize the ArtworkDownloader."""
        self.url = url
        self.download_path = download_path
        self.live_manager = live_manager
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
        self.artwork_id, self.data = self.fetch_artwork_data()
        if "illust" in self.data:
            self.process_artwork_from_data()

    def create_download_directory(self) -> str:
        """Create a directory to store the downloaded artwork."""
        page_count = self.artwork.get("pageCount")
        download_path = (
            Path(DOWNLOAD_FOLDER) / self.artwork_id
            if page_count > 1
            else self.download_path
        )
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
            self.live_manager.add_overall_task(
                description=self.artwork_id,
                num_tasks=images,
            )
            for image in range(images):
                task = self.live_manager.add_task(current_task=image)
                image_info = (self.artwork, image)
                task_info = (self.live_manager, task)
                future = executor.submit(
                    save_image_from_response,
                    image_info,
                    self.download_path,
                    task_info,
                )
                futures[future] = task
                manage_running_tasks(futures, self.live_manager)

    def process_artwork_gifs(self) -> None:
        """Download the GIF of the artwork."""
        self.live_manager.add_overall_task(
            description=self.artwork_id,
            num_tasks=1,
        )
        save_gif_from_response(
            self.artwork,
            self.download_path,
            (self.live_manager, 0),
        )


    def fetch_artwork_data(self) -> tuple:
        """Fetch the artwork data by making an HTTP request to the provided URL."""
        if not isinstance(self.url, str):
            logging.exception("The provided URL is not a string")
            sys.exit(1)

        response = requests.get(self.url, headers=HEADERS, timeout=10)
        if response.status_code != HTTP_STATUS_OK:
            response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        meta_content = soup.find("meta", {"id": "meta-preload-data"}).get("content")
        data = json.loads(meta_content)

        match = re.search(r"artworks/(\d+)", self.url)
        if not match:
            logging.exception("No artwork ID found")
            sys.exit(1)

        artwork_id = match.group(1)
        return artwork_id, data


def download_album(
    url: str,
    live_manager: LiveManager,
) -> None:
    """Download an album from the provided URL."""
    artwork_downloader = ArtworkDownloader(
        url=url,
        download_path=DOWNLOAD_FOLDER,
        live_manager=live_manager,
    )
    artwork_downloader.download()


def initialize_managers(*, disable_ui: bool = False) -> LiveManager:
    """Initialize and return the managers for progress tracking and logging."""
    progress_manager = ProgressManager(task_name="Album", item_description="File")
    logger_table = LoggerTable()
    return LiveManager(progress_manager, logger_table, disable_ui=disable_ui)


def main() -> None:
    """Run the application."""
    if len(sys.argv) != 2:
        script_name = Path(__file__).name
        message = f"Usage: python3 {script_name} <album_url>"
        logging.error(message)
        sys.exit(1)

    clear_terminal()
    url = sys.argv[1]

    live_manager = initialize_managers()
    with live_manager.live:
        download_album(url, live_manager)
        live_manager.stop()


if __name__ == "__main__":
    main()
