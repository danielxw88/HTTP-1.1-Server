import socket
import os
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8080
PUBLIC_DIR = Path("public").resolve()

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
}


def get_content_type(file_path: Path) -> str:
    return CONTENT_TYPES.get(file_path.suffix.lower(), "application/octet-stream")


def build_response(status_code: int, reason: str, body: bytes, content_type: str) -> bytes:
    headers = [
        f"HTTP/1.1 {status_code} {reason}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "",
        "",
    ]
    header_bytes = "\r\n".join(headers).encode("utf-8")
    return header_bytes + body


def build_html_response(status_code: int, reason: str, html: str) -> bytes:
    return build_response(status_code, reason, html.encode("utf-8"), "text/html; charset=utf-8")


def parse_request(request_data: bytes):
    try:
        text = request_data.decode("utf-8", errors="ignore")
        lines = text.split("\r\n")

        if not lines or len(lines[0].split()) != 3:
            return None, None, None, None

        method, path, version = lines[0].split()

        headers = {}
        for line in lines[1:]:
            if line == "":
                break
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()

        return method, path, version, headers
    except Exception:
        return None, None, None, None


def safe_resolve_path(url_path: str) -> Path | None:
    if "?" in url_path:
        url_path = url_path.split("?", 1)[0]

    if url_path == "/":
        url_path = "/index.html"

    relative_path = url_path.lstrip("/")
    requested_path = (PUBLIC_DIR / relative_path).resolve()

    try:
        requested_path.relative_to(PUBLIC_DIR)
    except ValueError:
        return None

    return requested_path


def handle_client(client_socket: socket.socket, client_address):
    print(f"[INFO] Connected by {client_address}")

    try:
        request_data = client_socket.recv(4096)
        if not request_data:
            print("[WARN] Empty request received")
            return

        print("[INFO] RAW REQUEST:")
        print(request_data.decode("utf-8", errors="ignore"))

        method, path, version, headers = parse_request(request_data)

        if not method or not path or not version:
            response = build_html_response(
                400,
                "Bad Request",
                "<html><body><h1>400 Bad Request</h1></body></html>",
            )
            client_socket.sendall(response)
            return

        print(f"[INFO] Parsed request: {method} {path} {version}")

        if version != "HTTP/1.1":
            response = build_html_response(
                400,
                "Bad Request",
                "<html><body><h1>400 Bad Request</h1><p>Only HTTP/1.1 is supported.</p></body></html>",
            )
            client_socket.sendall(response)
            return

        if method != "GET":
            response = build_html_response(
                405,
                "Method Not Allowed",
                "<html><body><h1>405 Method Not Allowed</h1></body></html>",
            )
            client_socket.sendall(response)
            return

        file_path = safe_resolve_path(path)

        if file_path is None:
            response = build_html_response(
                400,
                "Bad Request",
                "<html><body><h1>400 Bad Request</h1><p>Invalid path.</p></body></html>",
            )
            client_socket.sendall(response)
            return

        if not file_path.exists() or not file_path.is_file():
            response = build_html_response(
                404,
                "Not Found",
                "<html><body><h1>404 Not Found</h1></body></html>",
            )
            client_socket.sendall(response)
            print(f"[INFO] 404 Not Found: {file_path}")
            return

        with open(file_path, "rb") as f:
            body = f.read()

        content_type = get_content_type(file_path)
        response = build_response(200, "OK", body, content_type)
        client_socket.sendall(response)
        print(f"[INFO] 200 OK served: {file_path}")

    except Exception as e:
        print(f"[ERROR] {e}")
        try:
            response = build_html_response(
                500,
                "Internal Server Error",
                "<html><body><h1>500 Internal Server Error</h1></body></html>",
            )
            client_socket.sendall(response)
        except Exception:
            pass
    finally:
        client_socket.close()
        print(f"[INFO] Connection closed: {client_address}")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"[INFO] Server running at http://{HOST}:{PORT}")
    print(f"[INFO] Serving files from: {PUBLIC_DIR}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            handle_client(client_socket, client_address)
    except KeyboardInterrupt:
        print("\n[INFO] Server shutting down...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()