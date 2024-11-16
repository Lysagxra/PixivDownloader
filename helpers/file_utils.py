"""
This module provides utility functions for file input and output operations. It 
includes methods to read the contents of a file and to write content to a file, 
with optional support for clearing the file.
"""

def read_file(filename):
    """
    Reads the contents of a file and returns a list of its lines.

    Args:
        filename (str): The path to the file to be read.

    Returns:
        list: A list of lines from the file, with newline characters removed.
    """
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read().splitlines()

def write_file(filename, content='', mode='w'):
    """
    Writes or appends content to a specified file.

    Args:
        filename (str): The path to the file to be written to.
        content (str, optional): The content to write to the file.
                                 Defaults to an empty string.
        mode (str, optional): The mode for file operation.
                              'w' for overwrite (default) or 'a' for append.

    Raises:
        IOError: If an error occurs while writing to the file.
    """
    with open(filename, mode, encoding='utf-8') as file:
        file.write(f"{content}\n" if mode == 'a' else content)
