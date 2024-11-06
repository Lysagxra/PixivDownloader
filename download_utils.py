"""
This module provides functionality to download images and GIFs from Pixiv,
along with progress tracking for downloads. It includes functions to handle 
HTTP responses, save images, create GIFs from extracted frames, and display 
download progress using the Rich library.
"""

import os
import zipfile
import shutil

import requests
from PIL import Image

from helpers.pixiv_utils import construct_image_url, construct_gif_url

HOST_PAGE = "http://www.pixiv.net/"
CHUNK_SIZE = 64 * 1024
TIMEOUT = 10

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

def save_image_from_response(image_info, download_path, task_info):
    """
    Saves the downloaded image to the specified directory.

    Args:
        response (requests.Response): The HTTP response containing the image.
        image_url (str): The URL of the image.
        artwork (dict): The metadata of the artwork.
        download_path (str): The directory where the image should be saved.
        image (int): The page number of the image.

    Raises:
        ValueError: If the response status code indicates a failure.
    """
    (artwork, image) = image_info

    artwork_url = artwork.get('url')
    image_url = construct_image_url(artwork_url, image)

    response = requests.get(image_url, headers=ALT_HEADERS, timeout=TIMEOUT)
    if response.status_code not in (200, 403):
        raise ValueError(
            "Unable to download image, server responded with "
            f"status code: {response.status_code}"
        )

    artwork_id = artwork.get('id')
    file_extension = os.path.splitext(image_url)[-1]
    formatted_filename = (
        f"{artwork_id}_p{image}_master1200{file_extension}"
    )
    final_path = os.path.join(download_path, formatted_filename)

    download_with_progress(response, final_path, task_info)

def save_gif_from_response(artwork, download_path, task_info):
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

    def extract_gif(artwork_id, zip_path, download_path):
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

    artwork_url = artwork.get('url')
    gif_url = construct_gif_url(artwork_url)
    response = requests.get(gif_url, headers=ALT_HEADERS, timeout=TIMEOUT)

    if response.status_code not in (200, 403):
        raise ValueError(
            "Unable to download image, server responded with "
            f"status code: {response.status_code}"
        )

    artwork_id = artwork.get('id')
    formatted_filename = f"{artwork_id}.zip"
    zip_path = os.path.join(download_path, formatted_filename)

    download_with_progress(response, zip_path, task_info, is_gif=True)
    extract_gif(artwork_id, zip_path, download_path)

def manage_running_tasks(futures, job_progress):
    """
    Manages and updates the status of running tasks in a concurrent 
    execution environment.

    Parameters:
        futures (dict): A dictionary mapping futures to their 
                        corresponding tasks. Each future represents 
                        an asynchronous task.
        job_progress (Progress): An instance of a progress tracking 
                                 object used to manage and update 
                                 task visibility.
    """
    while futures:
        for future in list(futures.keys()):
            if future.running():
                task = futures.pop(future)
                job_progress.update(task, visible=True)

def download_with_progress(response, download_path, task_info, is_gif=False):
    """
    Downloads content from a response object and displays a progress bar.

    Parameters:
        response (requests.Response): The response object containing
                                      the content to be downloaded.
        download_path (str): The file path where the downloaded content should
                             be saved.
    """
    (job_progress, overall_progress, task, overall_task) = task_info
    file_size = int(response.headers.get('content-length', -1))
    total_downloaded = 0

    with open(download_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                file.write(chunk)
                total_downloaded += len(chunk)
                progress_percentage = (total_downloaded / file_size) * 100
                if not is_gif:
                    job_progress.update(task, completed=progress_percentage)

    if not is_gif:
        job_progress.update(task, completed=100, visible=False)
    overall_progress.advance(overall_task)
