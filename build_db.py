from parser import parse_docx
from embedding import (build_embedding_text,build_metadata,generate_embedding)
from vectorstore import (reset_collection,add_document)

def build_database():
    chunks = parse_docx("data/Soft Decoration Master Data Management User Manual.docx")

    collection = reset_collection()

    for i , chunk in enumerate(chunks):
        text = build_embedding_text(chunk)

        vector = generate_embedding(text)

        metadata = build_metadata(chunk)

        add_document(
            collection,
            f"chunk_{i}",
            text,
            vector,
            metadata
        )

        print(f"chunk_{i}"
          f"{chunk["Customer"]} -"
          f"{chunk["Subject"]}")
    print()
    print(f"database build: {len(chunks)} chunks")

if __name__ == "__main__":
    build_database()