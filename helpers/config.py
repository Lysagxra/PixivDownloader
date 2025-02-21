"""Configuration module for managing constants and settings used across the project.

These configurations aim to improve modularity and readability by consolidating settings
into a single location.
"""

ALREADY_DOWNLOADED = "already_downloaded.txt"  # File containing the list of already
                                               # downloaded URLs to prevent duplicates.
DOWNLOAD_FOLDER = "Downloads"                  # The folder where downloaded files will
                                               # be stored.
FILE = "URLs.txt"                              # The name of the file containing the
                                               # list of URLs to process.

IMAGE_ILLUST_TYPES = (0, 1)  # The types for static images illustrations.
GIF_ILLUST_TYPE = 2          # The type for GIF illustrations.

TITLE_COLOR = "light_cyan3"  # Color used for displaying titles.
TASK_COLOR = "light_cyan3"   # Color used for displaying task-related information.

MAX_WORKERS = 10        # Maximum number of concurrent workers for downloading.
CHUNK_SIZE = 16 * 1024  # The size of each chunk for downloading (16 KB).
TIMEOUT = 10            # Timeout duration for requests in seconds.

# HTTP status codes.
HTTP_STATUS_OK = 200

# Headers specifically tailored for download requests.
ALT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) "
        "Gecko/20100101 Firefox/115.0"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "http://www.pixiv.net/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Connection": "keep-alive",
}
