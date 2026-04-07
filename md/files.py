import os
import glob
from typing import List


def get_paths(collect_folder_path: str) -> List[str]:
    """Retrieve all Markdown (`.md`) file paths from the specified directory.

    Args:
        collect_folder_path (str): The path to the directory where Markdown files are located.

    Raises:
        FileNotFoundError: If the specified directory does not exist.

    Returns:
        List[str]: A list of full paths to all Markdown (`.md`) files in the directory.
                  Returns an empty list if no files are found.
    """

    if not os.path.exists(collect_folder_path):
        raise FileNotFoundError(f"{collect_folder_path} does not exist")

    return glob.glob(os.path.join(collect_folder_path, "*.md"))


def get_content(markdown_file_path: str) -> str:
    """Reads the content of a Markdown file and returns it as a string.

    Args:
        markdown_file_path (str): The path to the Markdown file to be read.

    Returns:
        str: The content of the Markdown file as a string.
    """

    with open(markdown_file_path, "rt") as reader:
        return reader.read()


def get_content_all(markdown_file_paths: List[str]) -> List[str]:
    """Reads the content of multiple Markdown files and returns their contents as a list of strings.

    Args:
        markdown_file_paths (List[str]): A list of paths to the Markdown files to be read.

    Returns:
        List[str]: A list of strings where each string is the content of the corresponding Markdown file.
    """

    return [
        get_content(markdown_file_path) for markdown_file_path in markdown_file_paths
    ]
