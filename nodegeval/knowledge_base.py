import os
import re

from collections import deque
from typing import List, Set

from nodegeval.files import MarkdownFile, Placeholder
from nodegeval.references import IncomingReference, OutgoingReference


def scrape(directory: str) -> List[str]:
    """Scrapes all markdown files (.md) from the given directory and its subdirectories.

    Args:
        directory (str): The root directory to start scraping from.

    Returns:
        List[str]: A list of absolute paths to all markdown files found in the directory and its subdirectories.
    """

    markdown_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))

    return markdown_files


def detect_references(text: str) -> List[str]:
    """Finds all references in the given text formatted as [[reference#section|display text]].
    Args:
    text (str): The input text to search for references.
    Returns:
        List[str]: A list of strings containing all the references found in the text.
                Each reference is the content inside the double brackets, without the brackets themselves.
    """
    references = re.findall(r"\[\[(.+?)\]\]", text)
    return references


class KnowledgeBase:
    """Knowledge base, created from markdown files."""

    def __init__(self, base_path: str, category_filter: str | None = None):
        """Initializes the KnowledgeBase with the given base path.

        Args:
            base_path (str): The root directory path where markdown files are located.
            category_filter (str, optional): Filter to only include markdown files
                belonging to the specified category. All references are still tracked, but filtered references receive the "filtered" property. Defaults to None (no filtering).
        """

        self.base_path: str = base_path
        self.markdown_files: List[MarkdownFile] = []
        markdown_file_paths: List[str] = scrape(self.base_path)

        for index, markdown_file_path in enumerate(markdown_file_paths):
            # Retain only the relative path so matching becomes easier
            relative_path = markdown_file_path.replace(self.base_path, "")
            markdown_file = MarkdownFile(
                markdown_file_path, relative_path, self.base_path, index
            )
            self.markdown_files.append(markdown_file)

        self.category_filter: str | None = category_filter

        self.compute_outgoing_neighbours()
        self.resolve_outgoing_neighbours()
        self.compute_incoming_neighbours()

    def resolve_file(self, text: str) -> int | None:
        """Resolves a reference to a markdown file if the reference matches a file in the collection.

        The reference is split into parts and compared against the relative path parts of each markdown.

        Args:
            text (str): The text to be resolved to a file index. This typically represents a relative file path or filename.

        Returns:
            int | None: The index of the matching markdown file if found, otherwise None.
        """

        reference_filename = text

        for markdown_file in self.markdown_files:
            match_reference_parts = reference_filename.split("/")
            match_reference_part_count = len(match_reference_parts)
            # Cannot match because lengths are not the same
            if len(markdown_file.parts) < match_reference_part_count:
                continue

            # Match found!
            if (
                markdown_file.parts[-match_reference_part_count:]
                == match_reference_parts
            ):
                return markdown_file.index
        else:
            return None

    def get_last_index(self) -> int:
        """Returns the index of the last markdown file in the collection, plus one. Used when adding new files to ensure they get a unique index.

        Returns:
            int: The index of the next available position.
        """

        return len(self.markdown_files)

    def compute_outgoing_neighbours(self):
        """Computes outgoing references (neighbours) for each markdown file.

        This method scans the content of each markdown file to find all references
        (links) to other files. Note that references are not yet resolved!
        """

        for markdown_file in self.markdown_files:
            relative_path = markdown_file.path
            if markdown_file.path[0] == "/":
                relative_path = markdown_file.path[1:]

            full_path = os.path.join(self.base_path, f"{relative_path}")

            with open(full_path, "rt") as reader:
                content = reader.read()
                references_text = detect_references(content)
                markdown_file.outgoing_neighbours = [
                    OutgoingReference.from_text(reference_text)
                    for reference_text in references_text
                ]

    def resolve_outgoing_neighbours(self):
        """Resolves the outgoing references (neighbours) for each markdown file.

        For each reference in a file's outgoing neigbhours list, this method attempts
        to find the corresponding target file in the knowledge base. If the target doesn't exist, a placeholder is created.
        """

        for markdown_file in self.markdown_files:
            for reference in markdown_file.outgoing_neighbours:
                reference_filename = reference.filename

                if reference_filename is None:
                    raise ValueError(
                        "Reference filename cannot be None for outgiong neighbours."
                    )

                resolved_id = self.resolve_file(reference_filename)
                if resolved_id is not None:
                    resolved_reference = self.markdown_files[resolved_id]

                    if resolved_reference.is_placeholder:
                        reference.refers_to_placeholder = True
                        reference.refers_to_index = resolved_reference.index
                    else:
                        reference.filtered = (
                            markdown_file.category == self.category_filter
                        )
                        reference.refers_to_index = resolved_id
                else:
                    # print(f"Creating placeholder for reference: {reference_filename}.")
                    placeholder = Placeholder(reference_filename, self.get_last_index())
                    self.markdown_files.append(placeholder)

                    reference.refers_to_placeholder = True
                    reference.refers_to_index = placeholder.index

    def compute_incoming_neighbours(self):
        """Computes incoming references (neighbours) for each markdown file.

        The computation works "inside out" by processing all outgoing references opf files. For each outgoing reference to another file (or placeholder), an incoming reference that points back to the original file is created.
        """

        for markdown_file in self.markdown_files:
            outgoing_neighbours = markdown_file.outgoing_neighbours

            for outgoing_reference in outgoing_neighbours:
                # bv verwijst naar naslagwerk
                incoming_reference = IncomingReference(markdown_file.filename)
                incoming_reference.refers_to_index = markdown_file.index
                incoming_reference.filtered = (
                    self.markdown_files[outgoing_reference.refers_to_index].category
                    == self.category_filter
                )

                self.markdown_files[
                    outgoing_reference.refers_to_index
                ].incoming_neighbours.append(incoming_reference)
