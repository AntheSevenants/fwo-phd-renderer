import os
from typing import Set, List, Union, TYPE_CHECKING

from nodegeval.references import OutgoingReference, IncomingReference


def split_all(path: str) -> List[str]:
    """Splits the given path into its constituent directory and file parts.

    Args:
        path (str): The path to be split, which can be an absolute or relative path.

    Returns:
        List[str]: A list of strings representing the directory and file parts of the path.
                For example, for the path "dir1/dir2/file.txt", it returns ["dir1", "dir2", "file"].
                The extension of the last part (if present) is removed.
                For absolute paths, the initial empty string is not included in the result.
    """

    all_parts = []

    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            # all_parts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            all_parts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            all_parts.insert(0, parts[1])

    # Remove extension
    if all_parts[-1][-3:] == ".md":
        all_parts[-1] = all_parts[-1][:-3]

    return all_parts


class MarkdownFile:
    """Represent a markdown file in the knowledge base."""

    def __init__(
        self, full_path: str | None, path: str, base_path: str | None, index: int
    ):
        """Initializes a markdown file given its path and index.

        Args:
            full_path (str): The absolute system path to the markdown file.
            path (str): The relative path to the markdown file (used for reference matching).
            base_path (str): Base path of the knowledge base.
            index (int): A unique identifier for the file within the knowledge base.
        """

        self.index = index
        self.full_path = full_path
        self.path = path
        self.base_path = base_path
        self.parts = split_all(self.path)
        self.category = self.compute_category()

        self.is_placeholder: bool = False

        self.outgoing_neighbours: List[OutgoingReference] = []
        self.incoming_neighbours: List[IncomingReference] = []

    @property
    def content(self) -> str:
        """Gets the raw text content of the markdown file.

        Returns:
            str: The text content of the markdown file.

        Raises:
            FileNotFoundError: If placeholder and path is none.
        """

        if self.full_path is not None:
            with open(self.full_path, "rt") as reader:
                content = reader.read()
                return content
        else:
            raise FileNotFoundError(
                "Cannot get content of placeholder, as placeholders does not exist"
            )

    @property
    def filename(self) -> str:
        """Gets the filename of the markdown file.

        Returns:
            str: The filename of the markdown file.
        """

        return self.parts[-1]

    def compute_category(self) -> str | None:
        """Computes the category of the markdown file. This corresponds to a Summarine "course".

        Returns:
            str: The category of the markdown file.
        """

        # Placeholders have no categories
        if isinstance(self, Placeholder):
            return None

        if self.base_path is None:
            return None

        parts_no = len(self.parts) - 1
        for level in range(len(self.parts)):
            reverse_level = parts_no - level

            # Recreate the full directory
            full_dir = os.path.join(self.base_path, *self.parts[: reverse_level + 1])
            if os.path.exists(os.path.join(full_dir, "meta.json")):
                return self.parts[reverse_level]

        return ""

    @property
    def outgoing_indices(self) -> Set[int]:
        """Gets the set of indices of files this file references (outgoing references).

        Only includes references that are not filtered out (when a category filter is active).

        Returns:
            Set[int]: Set of indices of referenced files, or an empty set
            if there are no valid outgoing references.
        """

        return set(
            [
                reference.refers_to_index
                for reference in self.outgoing_neighbours
                if reference.filtered
            ]
        )

    @property
    def incoming_indices(self) -> Set[int]:
        """Gets the set of indices of files that reference this file (incoming references).

        Only includes references that are not filtered out (when a category filter is active).

        Returns:
            Set[int]: Set of indices of files that reference this file, or an empty set
                     if there are no valid incoming references.
        """

        return set(
            [
                reference.refers_to_index
                for reference in self.incoming_neighbours
                if reference.filtered
            ]
        )

    @property
    def neighbours(self) -> Set[int]:
        """Gets the set of indices of all neighbouring files.

        This combines both outgoing and incoming indices, providing a complete
        set of connected files (direct references to and from this file).

        Returns:
            Set[int]: Set of indices of all neighbouring files, or an empty set if
                     there are no neighbours.
        """

        outgoing_indices = self.outgoing_indices
        incoming_indices = self.incoming_indices

        return outgoing_indices.union(incoming_indices)


class Placeholder(MarkdownFile):
    """A markdown file that was referenced, but does not exist yet.

    Args:
        MarkdownFile (MarkdownFile): MarkdownFile class as parent
    """

    def __init__(self, path: str, index: int):
        """Initializes a placeholder given its relative path and index.

        Args:
            path (str): The relative path that was given to refer to the future markdown file.
            index (int): A unique identifier for the placeholder within the knowledge base.
        """

        super().__init__(None, path, None, index)
        self.is_placeholder = True
