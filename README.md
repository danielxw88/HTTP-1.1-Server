# Micro HTTP/1.1 Server

## Overview
This project is a lightweight web server built from scratch using Python and the Berkeley Socket API. It manually parses HTTP/1.1 requests, serves static files, and returns valid HTTP responses.

## Features
- TCP socket server
- Manual HTTP/1.1 request parsing
- Static file serving from `public/`
- 200 OK
- 400 Bad Request
- 404 Not Found
- 405 Method Not Allowed
- 500 Internal Server Error

## Tech Stack
- Python 3
- socket module

## Project Structure
micro-http-server/
- server.py
- public/
  - index.html
  - about.html
  - style.css

## How to Run
1. Clone this repository
2. Open terminal in the project folder
3. Run:
   `python3 server.py`
4. Open browser:
   `http://127.0.0.1:8080/`

## Test URLs
- `/`
- `/about.html`
- `/missing.html`

## Limitations
- Supports GET only
- Supports HTTP/1.1 only
- Single-threaded server
