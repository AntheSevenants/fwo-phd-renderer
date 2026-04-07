import argparse
import os
import md.files
import nodegeval.knowledge_base
import nodegeval.phd

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
        "--tmp_path",
        type=str,
        default="tmp/",
        help="Path where temporary files will be stored",
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

    os.makedirs(args.tmp_path, exist_ok=True)

    # Go over each manuscript file in the PhD
    for manuscript_file in manuscript_files:
        manuscript_content = manuscript_file.markdown_file.content

        # Go over each reference to a Mondothèque note in the PhD
        for reference in manuscript_file.manuscript_references:
            # This is the original in-text reference
            # i.e. [[Agent-based model|agent-based model]]
            in_text_reference = f"[[{reference.reference.raw}]]"

            replacements = []
            # Go over all the references for this Mondothèque note
            for source_reference in reference.refers_to.source_references:
                # If the reference has no citation key, skip
                if source_reference.citation_key is None:
                    continue

                replacement = source_reference.citation_key
                if source_reference.page_range is not None:
                    replacement += f", {source_reference.page_range}"
                replacements.append(replacement)

            citation = "; ".join(replacements)
            full_replacement = f"{reference.reference.friendly_name} [{citation}]"

            manuscript_content = manuscript_content.replace(
                in_text_reference, full_replacement
            )

        os.makedirs(args.out_path, exist_ok=True)

        output_path = os.path.join(
            args.out_path, f"{manuscript_file.markdown_file.filename}.md"
        )
        with open(output_path, "wt") as writer:
            writer.write(manuscript_content)
