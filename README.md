# Pixiv Downloader

> A Python-based tool for downloading Pixiv albums. This tool reads a list of URLs from a file, checks against a record of already downloaded albums to avoid duplicates, and processes the downloads accordingly.

![Demo](https://github.com/Lysagxra/SimplePixivDownloader/blob/e3601bc3c697c281a2b3a468b9c86bc1f468e9b6/misc/Demo.gif)

## Features

- Downloads multiple files concurrently.
- Handles both single album and batch downloads.
- Avoid duplicats by comparing URLs against a record of already downloaded albums.
- Progress indication during downloads.
- Automatically creates a directory structure for organized storage.

## Dependencies

- Python 3
- `Pillow` - for image processing and manipulation.
- `BeautifulSoup` (bs4) - for HTML parsing
- `requests` - for HTTP requests
- `rich` - for progress display in the terminal.

## Directory Structure

```
project-root/
│ ├── url_utils               # Python script containing Pixiv URLs utility
│ ├── download_utils.py       # Python script containing Pixiv downloads utility
│ └── progress_utils.py       # Python script containing progress utility
├── album_downloader.py       # Python script to download from a Pixiv album URL
├── main.py                   # Main Python script to run the downloader
├── URLs.txt                  # Text file containing album URLs
└── already_downloaded.txt    # File to record downloaded albums
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Lysagxra/SimplePixivDownloader.git

2. Navigate to the project directory:
   ```bash
   cd SimplePixivDownloader

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

## Single Album Download

To download a single album from an URL, you can use `album_downloader.py`, running the script with a valid album URL.

### Usage
```bash
python3 album_downloader.py <album_url>
```

### Example
```
python3 album_downloader.py https://www.pixiv.net/en/artworks/118267586
```

## Batch Download

To batch download from multiple album URLs, you can use the `main.py` script. This script reads URLs from a file named `URLs.txt` and downloads each one using the album downloader.

### Usage

1. Create a file named `URLs.txt` in the root of your project, listing each URL on a new line.

2. Run the batch download script:
```
python3 main.py
```
3. The downloaded files will be saved in the `Downloads` directory.

## Logging

The application append the downloaded albums in a file named `already_downloaded.txt` to avoid duplicates.
