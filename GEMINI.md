# Project: bookworm

`bookworm` is a command-line interface (CLI) application built with Python.

## Core Functionality

The primary purpose of `bookworm` is to allow users to upload their books and ask questions about them. The tool manages the storage of the books and interacts with a Large Language Model (LLM) to provide answers.

## Technical Details

### Data Storage

When a book is uploaded, the following data is stored in a database:
- The full text of the book.
- Summaries of each chapter.
- Embeddings generated from either the chapter summaries or the full chapter text.

### Question Answering

When a user asks a question about a specific book, `bookworm` uses a Retrieval-Augmented Generation (RAG) approach:
1.  The user's question is used to find the most relevant chapters or summaries from the database (likely using the stored embeddings).
2.  A few of the most relevant chapters are selected and provided as context within a prompt to an LLM.
3.  The LLM uses this context to generate an answer to the user's question.

### LLM Integration

`bookworm` uses Gemini models for asking questions and embedding chapters.
