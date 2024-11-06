"""
This module provides functionality to download artwork albums from the
Pixiv platform. It handles various artwork types, including images and
GIFs, by fetching metadata, constructing appropriate URLs, and downloading
content while displaying download progress.
"""

import os
import sys
import re
import json
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from rich.live import Live

from helpers.progress_utils import create_progress_bar, create_progress_table
from helpers.download_utils import (
    save_image_from_response, save_gif_from_response, manage_running_tasks
)

SCRIPT_NAME = os.path.basename(__file__)
DOWNLOAD_FOLDER = "Downloads"
HOST_PAGE = "http://www.pixiv.net/"

MAX_WORKERS = 10
TASK_COLOR = "light_cyan3"

HEADERS = {'Referer': HOST_PAGE}
TIMEOUT = 10

class ArtworkDownloader:
    """
    A class used to download artwork from a given URL.

    Attributes:
        url (str): The URL of the artwork.
        download_path (str): The directory for saving the artwork.
        artwork (dict): The metadata of the artwork being downloaded.
        artwork_id (str): The ID of the artwork being downloaded.
        data (dict): Data fetched from the artwork page.
    """

    def __init__(self, url, download_path, overall_progress, job_progress):
        """
        Initializes the ArtworkDownloader with the given URL and the download
        directory.

        Args:
            url (str): The URL of the artwork.
            download_path (str, optional): The download directory for saving the
                                           artwork.
        """
        self.url = url
        self.download_path = download_path
        self.overall_progress = overall_progress
        self.job_progress = job_progress
        self.artwork = None
        self.artwork_id = None
        self.data = None

    def process_illust_data(self, illust_data):
        """
        Processes illustration data to extract and prepare artwork information.

        Parameters:
            illust_data (dict): A dictionary containing illustration data, 
                                including user illustrations.

        Returns:
            bool: True if the artwork was successfully processed; 
                  False otherwise.
        """
        user_illusts = illust_data['userIllusts']

        if 'userIllusts' in illust_data and self.artwork_id in user_illusts:
            self.artwork = illust_data['userIllusts'][self.artwork_id]
            self.download_path = self.create_download_directory()
            self.handle_artwork_type()
            return True

        return False

    def process_artwork_from_data(self):
        """
        Processes artwork data from the illustration dataset.
        """
        data_items = self.data['illust'].items()
        for (_, illust_data) in data_items:
            self.process_illust_data(illust_data)

    def download(self):
        """
        Downloads artwork by fetching its metadata and handling different
        artwork types. This method parses the metadata, identifies the artwork,
        and triggers downloading of either images or GIFs based on the
        artwork type.
        """
        (self.artwork_id, self.data) = fetch_artwork_data(self.url)

        if 'illust' in self.data:
            self.process_artwork_from_data()

    def create_download_directory(self):
        """
        Creates a directory to store the downloaded artwork based on the
        page count.

        Returns:
            str: The path to the created directory.
        """
        page_count = self.artwork.get('pageCount')

        if page_count > 1:
            download_path = os.path.join(DOWNLOAD_FOLDER, self.artwork_id)
        else:
            download_path = self.download_path

        os.makedirs(download_path, exist_ok=True)
        return download_path

    def handle_artwork_type(self):
        """
        Handles different types of artwork by checking if it is an image or GIF
        and processing accordingly.
        """
        illust_type = self.artwork.get('illustType')

        if illust_type in (0, 1):
            self.process_artwork_images()
        elif illust_type == 2:
            self.process_artwork_gifs()

    def process_artwork_images(self):
        """
        Downloads individual images from the artwork and saves them in the
        specified directory.
        """
        images = self.artwork.get('pageCount', 1)
        futures = {}

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            overall_task = self.overall_progress.add_task(
                f"[{TASK_COLOR}]{self.artwork_id}", total=images, visible=True
            )

            for image in range(images):
                task = self.job_progress.add_task(
                    f"[{TASK_COLOR}]Picture {image + 1}/{images}",
                    total=100, visible=False
                )

                image_info = (self.artwork, image)
                task_info = (
                    self.job_progress, self.overall_progress,
                    task, overall_task
                )

                future = executor.submit(
                    save_image_from_response,
                    image_info, self.download_path, task_info
                )
                futures[future] = task
                manage_running_tasks(futures, self.job_progress)

    def process_artwork_gifs(self):
        """
        Downloads the GIF of the artwork and saves it in the specified
        directory.
        """
        overall_task = self.overall_progress.add_task(
            f"[{TASK_COLOR}]{self.artwork_id}", total=1, visible=True
        )
        save_gif_from_response(
            self.artwork, self.download_path,
            (self.job_progress, self.overall_progress, 0, overall_task)
        )

def fetch_artwork_data(url):
    """
    Fetches the artwork data by making an HTTP request to the provided URL
    and parsing the response.

    Returns:
        tuple: A tuple containing the artwork ID (str) and the parsed
               data (dict).

    Raises:
        TypeError: If the URL is not a string.
        ValueError: If the artwork ID is not found in the URL.
        HTTPError: If the HTTP request fails with a status code other
                   than 200.
    """
    if not isinstance(url, str):
        raise TypeError('The provided URL is not a string')

    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

    if response.status_code != 200:
        response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    meta_content = soup.find(
        'meta', {'id': 'meta-preload-data'}
    ).get('content')
    data = json.loads(meta_content)

    match = re.search(r'artworks/(\d+)', url)

    if not match:
        raise ValueError('No artwork ID found')

    artwork_id = match.group(1)
    return artwork_id, data

def download_album(url, overall_progress, job_progress):
    """
    Downloads an album from the provided URL.

    Args:
        url (str): The URL of the album to download.

    Raises:
        ValueError: If the album ID cannot be retrieved from the URL.
    """
    artwork_downloader = ArtworkDownloader(
        url=url, download_path=DOWNLOAD_FOLDER,
        overall_progress=overall_progress, job_progress=job_progress
    )
    artwork_downloader.download()

def clear_terminal():
    """
    Clears the terminal screen based on the operating system.
    """
    commands = {
        'nt': 'cls',      # Windows
        'posix': 'clear'  # macOS and Linux
    }

    command = commands.get(os.name)
    if command:
        os.system(command)

def main():
    """
    The main entry point for the application.

    Raises:
        SystemExit: If the incorrect number of arguments is provided.
    """
    if len(sys.argv) != 2:
        print(f"Usage: python3 {SCRIPT_NAME} <album_url>")
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
