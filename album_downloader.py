"""
This module provides functionality to download artwork albums from the
Pixiv platform. It handles various artwork types, including images and
GIFs, by fetching metadata, constructing appropriate URLs, and downloading
content while displaying download progress.

Key Components:
- ArtworkDownloader: A class that manages the downloading process for a
  given artwork URL.
- Utility functions: Functions to read/write files, handle HTTP requests,
  and manage progress displays.

Constants:
- DOWNLOAD_FOLDER: The default folder where downloaded artworks will be
  saved.
- HEADERS: Default headers for HTTP requests to ensure proper content
  retrieval.

Usage:
Run the script from the command line, providing the URL of the album to
download as an argument. The downloaded content will be saved in the
Downloads folder, organized by artwork ID.
"""

import os
import sys
import re
import json
import zipfile
import shutil
import requests
from bs4 import BeautifulSoup
from PIL import Image
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    DownloadColumn,
    TextColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)

SCRIPT_NAME = os.path.basename(__file__)
DOWNLOAD_FOLDER = "Downloads"
CHUNK_SIZE = 1024

HOST_PAGE = "http://www.pixiv.net/"
HOST_ARTWORKS_PAGE = "http://www.pixiv.net/en/artworks"
HOST_ARTWORKS_PAGE_SECURE = "https://www.pixiv.net/en/artworks"

PIXIV_SEARCH_ILLUST = "https://www.pixiv.net/ajax/search/illustrations"
PIXIV_SEARCH_ARTWORKS = "https://www.pixiv.net/ajax/search/artworks"

HEADERS = {'Referer': HOST_PAGE}
ALT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) '
        'Gecko/20100101 Firefox/115.0'
    ),
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': HOST_PAGE,
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Connection': 'keep-alive',
}

COLORS = {
    'PURPLE': '\033[95m',
    'CYAN': '\033[96m',
    'DARKCYAN': '\033[36m',
    'BLUE': '\033[94m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
    'END': '\033[0m'
}

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

    def __init__(self, url, download_path):
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
        self.artwork = None
        self.artwork_id = None
        self.data = None

    def download(self):
        """
        Downloads artwork by fetching its metadata and handling different
        artwork types. This method parses the metadata, identifies the artwork,
        and triggers downloading of either images or GIFs based on the
        artwork type.
        """
        (self.artwork_id, self.data) = self.fetch_artwork_data()

        if 'illust' in self.data:
            for (_, illust_data) in self.data['illust'].items():
                if 'userIllusts' in illust_data and \
                    self.artwork_id in illust_data['userIllusts']:
                    self.artwork = illust_data['userIllusts'][self.artwork_id]
                    self.download_path = self.create_download_path()
                    self.handle_artwork_type()

    def fetch_artwork_data(self):
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
        if not isinstance(self.url, str):
            raise TypeError('The provided URL is not a string')

        response = requests.get(self.url, headers=HEADERS)

        if response.status_code != 200:
            response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        meta_content = soup.find(
            'meta', {'id': 'meta-preload-data'}
        ).get('content')
        data = json.loads(meta_content)

        match = re.search(r'artworks/(\d+)', self.url)

        if not match:
            raise ValueError('No artwork ID found')

        artwork_id = match.group(1)
        return artwork_id, data

    def create_download_path(self):
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
        for image in range(self.artwork.get('pageCount', 1)):
            artwork_url = self.artwork.get('url')
            url = construct_image_url(artwork_url, image)
            response = requests.get(url, stream=True, headers=HEADERS)
            save_image_from_response(
                response, url, self.artwork, self.download_path, image
            )

    def process_artwork_gifs(self):
        """
        Downloads the GIF of the artwork and saves it in the specified
        directory.
        """
        artwork_url = self.artwork.get('url')
        url = construct_gif_url(artwork_url)
        response = requests.get(url, stream=True, headers=HEADERS)
        save_gif_from_response(response, self.artwork, self.download_path)

def construct_image_url(artwork_url, image):
    """
    Constructs the image URL for downloading based on the artwork URL and
    page number.

    Args:
        artwork_url (str): The base URL of the artwork.
        image (int): The page number of the image.

    Returns:
        str: The modified URL for downloading the specific image.
    """
    url = re.sub(r'/c/250x250_80_a2/custom-thumb', '/img-master', artwork_url)
    url = re.sub(r'/c/250x250_80_a2/img-master', '/img-master', url)
    url = re.sub(r'_square1200.jpg$', '_master1200.jpg', url)
    url = re.sub(r'_custom1200.jpg$', '_master1200.jpg', url)
    url = re.sub(r'p[0-9]+', f'p{image}', url)
    return url

def construct_gif_url(artwork_url):
    """
    Constructs the GIF URL for downloading based on the artwork URL.

    Args:
        artwork_url (str): The base URL of the artwork.

    Returns:
        str: The modified URL for downloading the GIF.
    """
    url = re.sub(
        r'/c/250x250_80_a2/custom-thumb', '/img-zip-ugoira', artwork_url
    )
    url = re.sub(r'/c/250x250_80_a2/img-master', '/img-zip-ugoira', url)
    url = re.sub(r'_square1200.jpg$', '_ugoira600x600.zip', url)
    url = re.sub(r'_custom1200.jpg$', '_ugoira600x600.zip', url)
    return url

def progress_bar():
    """
    Creates and returns a progress bar for tracking download progress.

    Returns:
        Progress: A Progress object configured with relevant columns.
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        "-",
        TransferSpeedColumn(),
        "-",
        TimeRemainingColumn(),
        transient=True
    )

def download_with_progress(response, download_path):
    """
    Downloads content from a response object and displays a progress bar.

    Parameters:
        response (requests.Response): The response object containing
                                      the content to be downloaded.
        download_path (str): The file path where the downloaded content should
                             be saved.
    """
    file_size = int(response.headers.get('content-length', -1))

    with open(download_path, 'wb') as file:
        with progress_bar() as pbar:
            task = pbar.add_task("[cyan]Progress", total=file_size)

            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    file.write(chunk)
                    pbar.update(task, advance=len(chunk))

def save_image_from_response(response, url, artwork, download_path, image):
    """
    Saves the downloaded image to the specified directory.

    Args:
        response (requests.Response): The HTTP response containing the image.
        url (str): The URL of the image.
        artwork (dict): The metadata of the artwork.
        download_path (str): The directory where the image should be saved.
        image (int): The page number of the image.

    Raises:
        ValueError: If the response status code indicates a failure.
    """
    if response.status_code not in (200, 403):
        raise ValueError(
            "Unable to download image, server responded with "
            f"status code: {response.status_code}"
        )
        
    file_extension = os.path.splitext(url)[-1]
    formatted_filename = (
        f"{artwork.get('id')}_p{image}_master1200{file_extension}"
    )
    final_path = os.path.join(download_path, formatted_filename)
    
    print(f"\t[+] Downloading {formatted_filename}...")
    response = requests.get(url, headers=ALT_HEADERS)
    download_with_progress(response, final_path)

def save_gif_from_response(response, artwork, download_path):
    """
    Saves the downloaded GIF to the specified directory.

    Args:
        response (requests.Response): The HTTP response containing the GIF.
        artwork (dict): The metadata of the artwork.
        download_path (str): The directory where the GIF should be saved.

    Raises:
        ValueError: If the response status code indicates a failure.
    """
    def create_gif(extracted_folder, download_path, filename_gif):
        """
        Creates a GIF from the extracted frames and saves it.

        Args:
            extracted_folder (str): The folder containing the extracted
                                    image frames.
            download_path (str): The directory where the GIF should be saved.
            filename_gif (str): The name of the resulting GIF file.

        Returns:
            str: The path to the created GIF.
        """
        image_files = sorted([
            file for file in os.listdir(extracted_folder)
            if file.endswith(('.jpg', '.png', '.jpeg'))
        ])

        images = [
            Image.open(os.path.join(extracted_folder, image_file))
            for image_file in image_files
        ]

        gif_download_path = os.path.join(download_path, filename_gif)

        images[0].save(
            gif_download_path, save_all=True, append_images=images[1:],
            loop=0, duration=100
        )

    def extract_gif(zip_path, artwork_id, download_path):
        extracted_folder = os.path.join(
            download_path, f"{artwork_id}_extracted"
        )
        os.makedirs(extracted_folder, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_folder)

        filename_gif = f"{artwork_id}.gif"
        create_gif(extracted_folder, download_path, filename_gif)

        os.remove(zip_path)
        shutil.rmtree(extracted_folder)
        print(f"\t[+] Successfully extracted {filename_gif}")

    if response.status_code not in (200, 403):
        raise ValueError(
            "Unable to download image, server responded with "
            f"status code: {response.status_code}"
        )

    artwork_id = artwork.get('id')
    artwork_url = artwork.get('url')
    gif_url = construct_gif_url(artwork_url)

    formatted_filename = f"{artwork_id}.zip"
    final_path = os.path.join(download_path, formatted_filename)

    print(f"\t[+] Downloading {artwork_id}.gif...")
    response = requests.get(gif_url, headers=ALT_HEADERS)
    download_with_progress(response, final_path)
    extract_gif(final_path, artwork_id, download_path)

def get_album_id(url):
    """
    Extracts the album ID from the provided URL.

    Args:
        url (str): The URL from which to the ID.

    Returns:
        str: The extracted ID.

    Raises:
        ValueError: If the URL format is incorrect.
    """
    try:
        return url.split('/')[-1]

    except IndexError:
        raise ValueError("Invalid URL format.")

def download_album(url):
    """
    Downloads an album from the provided URL.

    Args:
        url (str): The URL of the album to download.

    Raises:
        ValueError: If the album ID cannot be retrieved from the URL.
    """
    album_id = get_album_id(url)
    print(f"\nDownloading Album: {COLORS['BOLD']}{album_id}{COLORS['END']}")
    artwork_downloader = ArtworkDownloader(
        url=url, download_path=DOWNLOAD_FOLDER
    )
    artwork_downloader.download()
    print("\t[\u2713] Download complete.")

def main():
    """
    The main entry point for the application.

    Raises:
        SystemExit: If the incorrect number of arguments is provided.
    """
    if len(sys.argv) != 2:
        print(f"Usage: python3 {SCRIPT_NAME} <album_url>")
        sys.exit(1)

    url = sys.argv[1]
    download_album(url)

if __name__ == "__main__":
    main()
