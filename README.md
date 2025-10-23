# Backend Wizards Stage 1: String Analyzer Service

## Description

A RESTful API built with FastAPI for analyzing strings, computing properties, and supporting filtering (including natural language queries). Uses in-memory storage.

## Endpoints

- **POST /strings**: Analyze and store a string.
- **GET /strings/{string_value}**: Retrieve a specific string.
- **DELETE /strings/{string_value}**: Delete a string.
- **GET /strings**: List strings with filters (query params: is_palindrome, min_length, max_length, word_count, contains_character).
- **GET /strings/filter-by-natural-language?query=...**: Filter using natural language.

See the task description for request/response examples.

## Setup and Local Run

1. Clone the repo: `git clone <repo-url>`
2. Create virtual environment `python -m venv venv`
3. Activate virtual enviroment `Windows (Git Bash / CMD)source venv/Scripts/activate macOS / Linuxsource venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the server: `uvicorn app:app --reload`
6. Access at `http://127.0.0.1:8000`. Use tools like Postman or curl for testing.
7. Docs: Auto-generated at `http://127.0.0.1:8000/docs` (Swagger UI).

## Dependencies

- FastAPI: Web framework
- Uvicorn: ASGI server
- Pydantic: Data validation

Install via `pip install -r requirements.txt`. No environment variables needed.

## Testing Notes

- Test endpoints with sample strings (e.g., "radar" for palindrome).
- Natural language supports examples like "all single word palindromic strings".
- Data is in-memory; restarts clear storage.

## Deployment

Hosted on Railway: [https://yourapp.railway.app](https://yourapp.railway.app)
