import argparse
import os
import md.files
import nodegeval.knowledge_base
import nodegeval.phd

AUTHOR_YEAR_TEXT_CITATION = "$author-year$"
AUTHOR_TEXT_CITATION = "$author$"
YEAR_TEXT_CITATION = "$year$"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="FWO PhD renderer - manuscript goes brr!"
    )
    parser.add_argument(
        "knowledge_base_path",
        type=str,
        help="Path to the knowledge base directory",
    )
    parser.add_argument(
        "--out_path",
        type=str,
        default="out/",
        help="Path where output files will be stored",
    )

    args = parser.parse_args()

    # This is the knowledge base we will compare the manuscript against
    knowledge_base = nodegeval.knowledge_base.KnowledgeBase(
        args.knowledge_base_path, "Mondothèque"
    )
    print("Knowledge base loaded")

    manuscript_files = [
        markdown_file
        for markdown_file in knowledge_base.markdown_files
        if markdown_file.category == "Manuscript"
    ]
    print("Manuscript files filtered")
    print(manuscript_files)

    manuscript_files = [
        nodegeval.phd.ManuscriptFile(manuscript_file, knowledge_base)
        for manuscript_file in manuscript_files
    ]

    os.makedirs(args.out_path, exist_ok=True)

    # Go over each manuscript file in the PhD
    for manuscript_file in manuscript_files:
        manuscript_content = manuscript_file.markdown_file.content

        # Go over each reference to a Mondothèque note in the PhD
        for reference in manuscript_file.manuscript_references:
            # This is the original in-text reference
            # i.e. [[Agent-based model|agent-based model]]
            in_text_reference = f"[[{reference.reference.raw}]]"
            source_references = reference.refers_to.source_references

            if len(source_references) == 0:
                error = f"{reference.reference.raw} refers to a document with zero source references"
                print(error)
                # raise ValueError(
                #     error
                # )

            in_text_citation = reference.reference.friendly_name in [
                AUTHOR_YEAR_TEXT_CITATION,
                AUTHOR_TEXT_CITATION,
                YEAR_TEXT_CITATION,
            ]
            if in_text_citation and len(source_references) >= 2:
                raise ValueError(
                    f"{reference.reference.raw} is a text citation but refers to more than one source reference"
                )

            if not in_text_citation:
                replacements = []
                # Go over all the references for this Mondothèque note
                for source_reference in source_references:
                    # If the reference has no citation key, skip
                    if source_reference.citation_key is None:
                        continue

                    replacement = source_reference.citation_key
                    if source_reference.page_range is not None:
                        replacement += f", {source_reference.page_range}"
                    replacements.append(replacement)

                citation = "; ".join(replacements)
                full_replacement = f"{reference.reference.friendly_name} [{citation}]"
            else:
                citation = f"{source_reference.citation_key}"
                if source_reference.page_range is not None:
                    citation += f" [{source_reference.page_range}]"

                full_replacement = f"{citation}"

            manuscript_content = manuscript_content.replace(
                in_text_reference, full_replacement
            )

        os.makedirs(args.out_path, exist_ok=True)

        output_path = os.path.join(
            args.out_path, f"{manuscript_file.markdown_file.filename}.md"
        )
        with open(output_path, "wt") as writer:
            writer.write(manuscript_content)
