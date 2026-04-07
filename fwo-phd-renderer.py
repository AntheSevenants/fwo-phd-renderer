import argparse
import md.files
import nodegeval.knowledge_base

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="FWO PhD renderer - manuscript goes brr!"
    )
    parser.add_argument(
        "manuscript_path",
        type=str,
        help="Path to the manuscript Markdown files",
    )
    parser.add_argument(
        "knowledge_base_path",
        type=str,
        help="Path to the knowledge base directory",
    )

    args = parser.parse_args()

    # This is the knowledge base we will compare the manuscript against
    knowledge_base = nodegeval.knowledge_base.KnowledgeBase(
        args.knowledge_base_path, "Mondothèque"
    )
    print("Knowledge base loaded")

    manuscript_files_paths = md.files.get_paths(args.manuscript_path)
    manuscript_files = [
        markdown_file
        for markdown_file in knowledge_base.markdown_files
        if markdown_file.full_path in manuscript_files_paths
    ]
    print("Manuscript files filtered")
    print(manuscript_files)

    # for index, manuscript_file_path in enumerate(manuscript_files_paths):
    #     relative_path = manuscript_file_path.replace(args.manuscript_path, "")
    #     manuscript_file = nodegeval.knowledge_base.MarkdownFile(
    #         manuscript_file_path, relative_path, index
    #     )
    # print("Manuscript files loaded")
