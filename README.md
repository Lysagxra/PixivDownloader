# Pixiv Downloader

> A Python-based tool for downloading Pixiv albums. This tool reads a list of URLs from a file, checks against a record of already downloaded albums to avoid duplicates, and processes the downloads accordingly.

![Demo](https://github.com/Lysagxra/PixivDownloader/blob/01e060c7bd40f0df1a45c85185955b48aa0e58e6/misc/Demo.gif)

## Features

- Downloads multiple files concurrently.
- Supports [batch downloading](https://github.com/Lysagxra/PixivDownloader?tab=readme-ov-file#batch-download) via a list of URLs.
- Tracks download progress with a progress bar.
- Avoid duplicats by comparing URLs against a record of already downloaded albums.
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
├── helpers/
│ ├── managers/
│ │ ├── live_manager.py      # Manages a real-time live display
│ │ ├── log_manager.py       # Manages real-time log updates
│ │ └── progress_manager.py  # Manages progress bars
│ ├── download_utils.py      # Utilities for managing the download process
│ ├── file_utils.py          # Utilities for managing file operations
│ ├── general_utils.py       # Miscellaneous utility functions
│ └── pixiv_utils            # Functions for handling Pixiv-related tasks
├── album_downloader.py      # Module for downloading Pixiv albums
├── main.py                  # Main script to run the downloader
└── URLs.txt                 # Text file containing album URLs
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Lysagxra/PixivDownloader.git
```

2. Navigate to the project directory:

```bash
cd PixivDownloader
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Single Album Download

To download a single album from an URL, you can use `album_downloader.py`, running the script with a valid album URL.

### Usage

```bash
python3 album_downloader.py <album_url>
```

### Example

```
python3 album_downloader.py https://www.pixiv.net/en/artworks/122835267
```

## Batch Download

To batch download from multiple album URLs, you can use the `main.py` script. This script reads URLs from a file named `URLs.txt` and downloads each one using the album downloader.

### Usage

1. Create a file named `URLs.txt` in the root of your project, listing each URL on a new line.

- Example of `URLs.txt`:

```
https://www.pixiv.net/en/artworks/123398947
https://www.pixiv.net/en/artworks/123399029
https://www.pixiv.net/en/artworks/123399604
```

- Ensure that each URL is on its own line without any extra spaces.
- You can add as many URLs as you need, following the same format.

2. Run the batch download script:

```
python3 main.py
```

3. The downloaded files will be saved in the `Downloads` directory.

## Logging

The application append the downloaded albums in a file named `already_downloaded.txt` to avoid duplicates.
