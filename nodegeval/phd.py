import re
from typing import List

from nodegeval.files import MarkdownFile, Placeholder
from nodegeval.knowledge_base import KnowledgeBase
from nodegeval.references import OutgoingReference


def get_mondotheque_entry(reference: OutgoingReference, knowledge_base: KnowledgeBase):
    # Retrieve the markdown file object from the parent knowledge base
    markdown_file: MarkdownFile = knowledge_base.markdown_files[
        reference.refers_to_index
    ]
    # Then create a mondotheque file form this markdown file
    return MondothequeFile(markdown_file, knowledge_base)


def find_citation_key(md_content: str) -> str | None:
    for line in md_content.split("\n"):
        match = re.search(r"^citation_key:\s*(@[a-z0-9_.-]+)$", line)
        if match:
            citation_key = match.group(1)
            return citation_key
    return None


def find_page_range(md_content: str, section: str) -> str | None:
    lines = md_content.split("\n")

    # First, find the line that matches the section
    for i, line in enumerate(lines):
        if re.match(rf"^#+\s*{section}", line):
            # Now look for $p=...$ in lines above this one
            for j in range(i - 1, -1, -1):
                match = re.search(r"\$p=([^$]+)\$", lines[j])
                if match:
                    return match.group(1)
            # No $p=...$ found above
            return None
    # Section not found
    return None


class ManuscriptReference:
    def __init__(self, reference: OutgoingReference, knowledge_base: KnowledgeBase):
        self.refers_to = get_mondotheque_entry(reference, knowledge_base)
        self.reference = reference


class ManuscriptFile:
    """A PhD manuscript file"""

    def __init__(self, markdown_file: MarkdownFile, knowledge_base: KnowledgeBase):
        self.markdown_file: MarkdownFile = markdown_file
        self.knowledge_base: KnowledgeBase = knowledge_base
        self.manuscript_references: List[ManuscriptReference] = []

        self.compute_manuscript_references()

    def compute_manuscript_references(self):
        for reference in self.markdown_file.outgoing_neighbours:
            # Skip placeholders
            if reference.refers_to_placeholder:
                continue

            self.manuscript_references.append(
                ManuscriptReference(reference, self.knowledge_base)
            )


class MondothequeReference:
    def __init__(self, reference: OutgoingReference, knowledge_base: KnowledgeBase):
        self.reference = reference
        self.refers_to = knowledge_base.markdown_files[reference.refers_to_index]
        self.citation_key = find_citation_key(self.refers_to.content)
        self.page_range = find_page_range(
            self.refers_to.content, self.reference.section
        )

        if self.citation_key is not None:
            self.year = self.citation_key[-4:]
        else:
            self.year = None


class MondothequeFile:
    """A Mondotheque file"""

    def __init__(self, markdown_file: MarkdownFile, knowledge_base: KnowledgeBase):
        self.markdown_file = markdown_file
        self.knowledge_base = knowledge_base
        self.source_references: List[MondothequeReference] = []

        self.compute_source_references()

    def compute_source_references(self):
        for reference in self.markdown_file.outgoing_neighbours:
            if reference.refers_to_placeholder:
                continue

            referenced_file = self.knowledge_base.markdown_files[
                reference.refers_to_index
            ]
            if referenced_file.category != "Mondothèque":
                self.source_references.append(
                    MondothequeReference(reference, self.knowledge_base)
                )
