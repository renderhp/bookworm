import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def extract_chapters_from_epub(epub_path, output_dir=".", book_id=None, insert_chapter_func=None, genai_model=None, embedding_model_name=None, chapter_limit=None):
    """
    Extracts chapters from an EPUB file and saves them as plain text files or inserts them into a database.

    Args:
        epub_path (str): The path to the EPUB file.
        output_dir (str): The directory to save the extracted chapter files (if not inserting into DB).
        book_id (int, optional): The ID of the book in the database. Required if insert_chapter_func is provided.
        insert_chapter_func (function, optional): A function to insert chapter content into the database.
    """
    os.makedirs(output_dir, exist_ok=True)
    book = epub.read_epub(epub_path)
    chapters = []
    for i, item in enumerate(book.get_items()):
        if chapter_limit and i >= chapter_limit:
            break
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.content, 'html.parser')
            text = soup.get_text()
            # Filter out chapters with less than 100 words
            if len(text.split()) >= 100:
                chapters.append((item.file_name, text))
            else:
                print(f"Skipping short chapter: {item.file_name} (less than 100 words)")

    if insert_chapter_func and book_id is not None:
        for i, (file_name, content) in enumerate(chapters):
            embedding = None
            if genai_model and embedding_model_name:
                try:
                    response = genai_model.embed_content(model=embedding_model_name, content=content)
                    embedding = response['embedding']
                except Exception as e:
                    print(f"Error generating embedding for chapter {i+1}: {e}")
            insert_chapter_func(book_id, i + 1, content, embedding)
            print(f"Inserted chapter {i+1} into DB.")
    else:
        # Save chapters to files (this part can be refined later)
        for i, (file_name, content) in enumerate(chapters):
            # Create a more readable filename for the chapter
            chapter_filename = f"chapter_{i+1}.txt"
            with open(f"{output_dir}/{chapter_filename}", "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Extracted chapter: {chapter_filename}")

    print(f"Successfully processed {len(chapters)} chapters from {epub_path}")

if __name__ == "__main__":
    # Example usage (for testing purposes)
    # You would typically call this from main.py
    # extract_chapters_from_epub("path/to/your/book.epub", "output_chapters")
    pass