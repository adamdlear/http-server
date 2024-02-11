import os
import mimetypes

from TCPServer import TCPServer
from HTTPRequest import HTTPRequest

class HTTPServer(TCPServer):
    headers = {
        'Server': 'CrudeServer',
        'Content-Type': 'text/html'
    }

    status_codes = {
        200: 'OK',
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not found',
        408: 'Request Timeout',
        500: 'Internal Server Error',
        501: 'Not Implemented',
        502: 'Bad Gateway',
        504: 'Gateway Timeout',
    }

    def response_line(self, status_code):
        """
        Returns the response line
        """
        reason = self.status_codes[status_code]
        line = f"HTTP/1.1 {status_code} {reason}\r\n"

        return line.encode()

    def response_headers(self, extra_headers=None):
        """
        Returns the response headers
        """
        headers_copy = self.headers.copy()
        if extra_headers:
            headers_copy.update(extra_headers)
        headers = ""
        for h in headers_copy:
            headers += f"{h}: {headers_copy[h]}\r\n"
        return headers.encode()

    def handle_request(self, data):
        request = HTTPRequest(data)
        try:
            handler = getattr(self, f'handle_{request.method}')
        except AttributeError:
            handler = self.HTTP_501_handler
        response = handler(request)
        return response

    def HTTP_501_handler(self, request):
        response_line = self.response_line(status_code=501)
        response_headers = self.response_headers()
        blank_line = b"\r\n"
        response_body = b"<h1>501 Not Implemented</h1>"
        return b"".join([response_line, response_headers, blank_line, response_body])

    def handle_GET(self, request):
        filename = request.uri.strip('/')

        if os.path.exists(filename):
            response_line = self.response_line(status_code=200)
            content_type = mimetypes.guess_type(filename)[0] or 'text/html'
            extra_headers = {'Content-Type': content_type}
            response_headers = self.response_headers(extra_headers)
            with open(filename, 'rb') as f:
                response_body = f.read()
        else:
            response_line = self.response_line(status_code=404)
            response_headers = self.response_headers()
            response_body = b"<h1>404 Not Found</h1>"

        blank_line = b"\r\n"

        return b"".join([response_line, response_headers, blank_line, response_body])
