import socket
import json
import gc

def quote(string):
    string = string.replace("&quot;", "\"")
    string = string.replace("&amp;", "&")

    visible_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-/=?&%"
    encoded = ""

    for c in string:
        if c in visible_chars:
            encoded += c
        elif c == " ":
            encoded += "+"
        else:
            encoded_bytes = bytes(c, "ascii")
            for b in encoded_bytes:
                encoded += "%" + hex(b)[2:].upper()

    return encoded

BLOCK_SIZE = 512

GET_HEADER_TEMPLATE = """GET /{path} HTTP/1.1\r\nAccept-Encoding: identity\r\nHost: {host}\r\nConnection: keep-alive\r\n\r\n"""

POST_HEADER_TEMPLATE = """POST /{path} HTTP/1.1\r\nAccept-Encoding: identity\r\nContent-Length: {content_length}\r\nHost: {host}\r\nConnection: keep-alive\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n"""

def http_request(response_handler, url, method, content=""):
    _, _, host, path = url.split("/", 3)
    host, port = host.split(":")
    addr = socket.getaddrinfo(host, int(port))[0][-1]

    header = None

    if method == "GET":
        header = GET_HEADER_TEMPLATE.format(path=quote(path), host=host)
    elif method == "POST":
        header = POST_HEADER_TEMPLATE.format(path=quote(path), host=host, content_length=len(content))
    else:
        return

    s = socket.socket()
    s.settimeout(5)
    s.connect(addr)
    s.send(bytes(header + content, "ascii"))

    response = ""

    content_mode = False
    content_length = 0
    content_counter = 0

    while content_counter < content_length or not content_mode:
        data = s.recv(BLOCK_SIZE)

        if not data:
            break

        response += str(data, "utf8")

        if content_mode:
            content_counter += len(data)

        if "\n" in response:
            lines = response.split("\n")
            response = lines[-1]

            for i in range(len(lines) - 1):
                if len(lines[i]) == 0 or lines[i] == "\r" and not content_mode:
                    content_mode = True

                if "Content-Length:" in lines[i] and not content_mode:
                    content_length = int(lines[i].split("Content-Length:")[1])

                if content_mode:
                    if not response_handler(lines[i]):
                        return

    # flush the rests
    response_handler(response)

    s.close()

def http_get(response_handler, url):
    http_request(response_handler, url, "GET", "")

def http_post(response_handler, url, content=""):
    http_request(response_handler, url, "POST", content)

