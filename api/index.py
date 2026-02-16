from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.error
import json
import os

YCLIENTS_API = "https://api.yclients.com/api/v1"
SECRET = os.environ.get("PROXY_SECRET", "vdohvydoh2026")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def do_PUT(self):
        self._handle("PUT")

    def do_DELETE(self):
        self._handle("DELETE")

    def _handle(self, method):
        if self.headers.get("X-Proxy-Secret") != SECRET:
            self._respond(403, {"error": "forbidden"})
            return

        # /api?path=/records/123&other=params -> extract path param
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        api_path = params.get("path", [""])[0]

        if not api_path:
            self._respond(400, {"error": "missing path param"})
            return

        # Rebuild query without our 'path' param
        query_parts = []
        for k, vs in params.items():
            if k != "path":
                for v in vs:
                    query_parts.append(f"{k}={v}")
        query_string = "&".join(query_parts)

        url = f"{YCLIENTS_API}{api_path}"
        if query_string:
            url += f"?{query_string}"

        headers = {}
        for key in ["Accept", "Authorization", "Content-Type"]:
            val = self.headers.get(key)
            if val:
                headers[key] = val

        body = None
        if method in ("POST", "PUT"):
            length = int(self.headers.get("Content-Length", 0))
            if length > 0:
                body = self.rfile.read(length)

        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            resp = urllib.request.urlopen(req, timeout=25)
            data = resp.read()
            self._respond(resp.status, None, data)
        except urllib.error.HTTPError as e:
            self._respond(e.code, None, e.read())
        except Exception as e:
            self._respond(502, {"error": str(e)})

    def _respond(self, code, obj=None, raw=None):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if raw:
            self.wfile.write(raw)
        elif obj:
            self.wfile.write(json.dumps(obj).encode())
