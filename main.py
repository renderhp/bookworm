import argparse
import google.generativeai as genai
import numpy as np

from parser import extract_chapters_from_epub
from database import (
    init_db,
    set_api_key,
    get_api_key,
    insert_book,
    insert_chapter,
    get_book_by_title,
    get_chapters_for_book,
    purge_data,
)
from ebooklib import epub


def parse_book(args):
    """Parses a book and stores its content."""
    api_key = get_api_key()
    if not api_key:
        print("API key not configured. Please run 'configure' command first.")
        return

    print(f"Parsing book: {args.path}")
    try:
        book = epub.read_epub(args.path)
        title = (
            book.get_metadata("DC", "title")[0][0]
            if book.get_metadata("DC", "title")
            else "Unknown Title"
        )
        author = (
            book.get_metadata("DC", "creator")[0][0]
            if book.get_metadata("DC", "creator")
            else "Unknown Author"
        )
    except Exception as e:
        print(f"Error reading EPUB metadata: {e}. Using default title and author.")
        title = "Unknown Title"
        author = "Unknown Author"

    genai.configure(api_key=api_key)
    llm_model = genai.GenerativeModel("gemini-2.5-flash")

    book_id = insert_book(title, author, args.path)
    if book_id:
        print(f"Book '{title}' by {author} added to DB with ID: {book_id}")
        extract_chapters_from_epub(
            args.path,
            args.output_dir,
            book_id=book_id,
            insert_chapter_func=insert_chapter,
            genai_model=genai,
            embedding_model_name="gemini-embedding-001",
            chapter_limit=None,
            llm_model=llm_model,
        )
    else:
        print(
            f"Failed to add book {args.path} to the database. It might already exist."
        )


import google.generativeai as genai


def ask_question(args):
    """Asks a question about a book."""
    api_key = get_api_key()
    if not api_key:
        print("API key not configured. Please run 'configure' command first.")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    embedding_model = genai.GenerativeModel("gemini-embedding-001")

    book_info = get_book_by_title(args.book_title)
    if book_info:
        book_id, title, author, file_path = book_info
        print(f"Asking about book: {title} by {author}")
        chapters = get_chapters_for_book(book_id)
        if chapters:
            # Embed the user's question
            question_embedding_response = genai.embed_content(
                model="gemini-embedding-001", content=args.question
            )
            question_embedding = np.array(question_embedding_response["embedding"])

            chapter_similarities = []
            for chapter_number, content, embedding, summary in chapters:
                if embedding:
                    chapter_embedding = np.array(embedding)
                    similarity = np.dot(question_embedding, chapter_embedding) / (
                        np.linalg.norm(question_embedding)
                        * np.linalg.norm(chapter_embedding)
                    )
                    chapter_similarities.append((similarity, content))

            chapter_similarities.sort(key=lambda x: x[0], reverse=True)
            top_chapters = [content for similarity, content in chapter_similarities[:5]]

            context = "\n\n".join(top_chapters)
            prompt = f"Given the following chapters from the book:\n\n{context}\n\nAnswer the following question: {args.question}. If you can not get the answer to the question from the context, say so, do not make things up!"
            try:
                response = model.generate_content(prompt)
                print("\nAnswer:")
                print(response.text)
            except Exception as e:
                print(f"Error generating response from LLM: {e}")
        else:
            print(f"No chapters found for {title}.")
    else:
        print(f"Book '{args.book_title}' not found in the database.")


def configure_api_key(args):
    """Configures the API key."""
    api_key = input("Enter your Gemini API key: ")
    set_api_key(api_key)
    print("API key configured successfully.")


def purge_command(args):
    """Purges all book and chapter data from the database."""
    purge_data()


def main():
    init_db()
    parser = argparse.ArgumentParser(description="Bookworm CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse a book")
    parse_parser.add_argument("path", help="Path to the EPUB file")
    parse_parser.add_argument(
        "--output-dir", default="chapters", help="Directory to save extracted chapters"
    )
    parse_parser.set_defaults(func=parse_book)

    # Ask command
    ask_parser = subparsers.add_parser("ask", help="Ask a question about a book")
    ask_parser.add_argument("book_title", help="Title of the book to ask about")
    ask_parser.add_argument("question", help="The question to ask about the book")
    ask_parser.set_defaults(func=ask_question)

    # Configure command
    configure_parser = subparsers.add_parser("configure", help="Configure API key")
    configure_parser.set_defaults(func=configure_api_key)

    # Purge command
    purge_parser = subparsers.add_parser(
        "purge", help="Purge all book and chapter data"
    )
    purge_parser.set_defaults(func=purge_command)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
