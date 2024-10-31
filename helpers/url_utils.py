"""
This module provides functions to generate specific URLs for accessing
images and GIFs associated with artworks on Pixiv. The URL construction
is based on the artwork's base URL and the desired image page number.
"""

import re

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
