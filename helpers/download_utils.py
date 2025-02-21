"""Module that provides functionality to download images and GIFs from Pixiv.

It includes functions to handle HTTP responses, save images, create GIFs from extracted
frames, and display download progress using the Rich library.
"""

import logging
import os
import shutil
import sys
import zipfile
from pathlib import Path

import requests
from PIL import Image
from requests import Response
from rich.progress import Progress

from helpers.pixiv_utils import generate_gif_url, generate_image_url

from .config import ALT_HEADERS, CHUNK_SIZE, TIMEOUT


def save_image_from_response(
    image_info: tuple,
    download_path: str,
    task_info: tuple,
) -> None:
    """Save the downloaded image to the specified directory."""
    artwork, image = image_info
    artwork_url = artwork.get("url")
    image_url = generate_image_url(artwork_url, image)

    response = requests.get(image_url, headers=ALT_HEADERS, timeout=TIMEOUT)
    if response.status_code not in (200, 403):
        message = (
            "Unable to download image, "
            f"server responded with status code: {response.status_code}"
        )
        logging.exception(message)
        sys.exit(1)

    artwork_id = artwork.get("id")
    file_extension = os.path.splitext(image_url)[-1]
    formatted_filename = f"{artwork_id}_p{image}_master1200{file_extension}"
    final_path = Path(download_path) / formatted_filename
    download_with_progress(response, final_path, task_info)


def save_gif_from_response(artwork: dict, download_path: str, task_info: tuple) -> None:
    """Save the downloaded GIF to the specified directory."""

    def create_gif(extracted_folder: str, download_path: str, filename_gif: str) -> str:
        """Create a GIF from the extracted frames and saves it."""
        image_files = sorted(
            [
                file
                for file in os.listdir(extracted_folder)
                if file.endswith((".jpg", ".png", ".jpeg"))
            ],
        )

        images = [
            Image.open(Path(extracted_folder) / image_file)
            for image_file in image_files
        ]

        gif_download_path = Path(download_path) / filename_gif
        images[0].save(
            gif_download_path,
            save_all=True,
            append_images=images[1:],
            loop=0,
            duration=100,
        )

    def extract_gif(artwork_id: str, zip_path: str, download_path: str) -> None:
        extracted_folder = Path(download_path) / f"{artwork_id}_extracted"
        Path(extracted_folder).mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extracted_folder)

        filename_gif = f"{artwork_id}.gif"
        create_gif(extracted_folder, download_path, filename_gif)

        Path(zip_path).unlink()
        shutil.rmtree(extracted_folder)

    artwork_url = artwork.get("url")
    gif_url = generate_gif_url(artwork_url)
    response = requests.get(gif_url, headers=ALT_HEADERS, timeout=TIMEOUT)

    if response.status_code not in (200, 403):
        message = (
            "Unable to download image, server responded with "
            f"status code: {response.status_code}"
        )
        logging.exception(message)
        sys.exit(1)

    artwork_id = artwork.get("id")
    formatted_filename = f"{artwork_id}.zip"
    zip_path = Path(download_path) / formatted_filename

    download_with_progress(response, zip_path, task_info, is_gif=True)
    extract_gif(artwork_id, zip_path, download_path)


def manage_running_tasks(futures: dict, job_progress: Progress) -> None:
    """Manage and updates the status of running tasks."""
    while futures:
        for future in list(futures.keys()):
            if future.running():
                task = futures.pop(future)
                job_progress.update(task, visible=True)


def download_with_progress(
    response: Response, download_path: str, task_info: tuple, *, is_gif: bool = False,
) -> None:
    """Download content from a response object and displays a progress bar."""
    job_progress, overall_progress, task, overall_task = task_info
    file_size = int(response.headers.get("Content-Length", -1))
    total_downloaded = 0

    with Path(download_path).open("wb") as file:
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
