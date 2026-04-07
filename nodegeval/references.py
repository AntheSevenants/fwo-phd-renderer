from typing import TYPE_CHECKING


class ReferenceType:
    INCOMING = 0
    OUTGOING = 1


class Reference:
    def __init__(self, filename: str):
        self.filename = filename

        self.refers_to_placeholder: bool = False
        self.refers_to_index: int
        self.filtered: bool = True


class IncomingReference(Reference):
    def __init__(self, filename: str):
        super().__init__(filename)


class OutgoingReference(Reference):
    def __init__(
        self,
        filename: str,
        section: str,
        friendly_name: str,
        raw: str,
        ref_type=ReferenceType.OUTGOING,
    ):
        """Initializes a reference to a section in another file or placeholder.

        Args:
            filename (str): The relative path of the markdown file being referenced. Defaults to None.
            section (str): The section within the file, if any. Defaults to None.
            friendly_name (str): The display name for the reference. Defaults to None.
            raw (str): The original text of the reference as it appeared in the source. Defaults to None.
            ref_type (ReferenceType, optional): Type of reference (OUTGOING, INCOMING).
                Defaults to ReferenceType.OUTGOING.

        The reference is initially not marked as pointing to a placeholder, has no
        resolved index, and is marked as filtered (until resolved by the knowledge base).
        """

        super().__init__(filename)

        self.section = section
        self.friendly_name = friendly_name
        self.raw = raw

    @classmethod
    def from_text(cls, text: str):
        """Creates a Reference instance from a formatted reference text string.

        The text is expected to contain the filename, optionally followed by a section
        (indicated by '#') and a friendly name (indicated by '|').

        Args:
            text (str): The reference text in format: "filename#section|friendly_name"

        Raises:
            ValueError: If the filename is empty.

        Returns:
            Reference: A newly created Reference object with the parsed components.
        """

        filename = []
        section = []
        friendly_name = []

        current_pointer = filename
        for character in text:
            if character == "#":
                current_pointer = section
                continue
            elif character == "|":
                current_pointer = friendly_name
                continue
            else:
                current_pointer.append(character)

        filename = "".join(filename)
        section = "".join(section)
        friendly_name = "".join(friendly_name)

        if len(filename) == 0:
            raise ValueError(f"Filename cannot be empty. Detected text: {text}")

        instance = cls(filename, section, friendly_name, text, ReferenceType.OUTGOING)
        return instance
