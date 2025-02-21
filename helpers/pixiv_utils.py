"""Module to generate URLs for accessing images and GIFs of artworks on Pixiv."""

import re


def generate_image_url(artwork_url: str, image: int) -> str:
    """Generate the image URL for downloading based on the artwork URL."""
    # Adjust the base URL to point to the image master directory
    url = re.sub(r"/c/250x250_80_a2/custom-thumb", "/img-master", artwork_url)
    url = re.sub(r"/c/250x250_80_a2/img-master", "/img-master", url)

    # Modify file name to ensure it's the highest quality image (master1200)
    url = re.sub(r"(_square1200|_custom1200)\.jpg$", "_master1200.jpg", url)

    # Replace page number placeholder with the specified image page number
    return re.sub(r"p\d+", f"p{image}", url)


def generate_gif_url(artwork_url: str) -> str:
    """Generate the GIF URL for downloading based on the artwork URL."""
    # Replace custom-thumb and img-master paths with img-zip-ugoira
    url = re.sub(r"/c/250x250_80_a2/custom-thumb", "/img-zip-ugoira", artwork_url)
    url = re.sub(r"/c/250x250_80_a2/img-master", "/img-zip-ugoira", url)

    # Merge the two re.sub calls for _square1200.jpg and _custom1200.jpg
    return re.sub(r"_(square1200|custom1200)\.jpg$", "_ugoira600x600.zip", url)
