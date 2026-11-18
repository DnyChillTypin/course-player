import os, sys, mimetypes, urllib.parse, re
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
HERE = os.path.dirname(os.path.abspath(__file__))
COURSE = os.path.join(os.path.dirname(HERE), 'packt-data-governance-ai-governance-the-complete-guide-i0wqi')


class H(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = urllib.parse.unquote(urllib.parse.urlparse(path).path)
        base, p = (COURSE, p[7:]) if p.startswith('/media/') else (HERE, p)
        full = os.path.normpath(os.path.join(base, p.lstrip('/')))
        if not full.startswith(base):
            return os.path.join(HERE, '404')
        return full

    def do_GET(self):
        self.serve(True)

    def do_HEAD(self):
        self.serve(False)

    def serve(self, body):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            path = os.path.join(path, 'index.html')
        if not os.path.isfile(path) or os.path.basename(path) in ('build.py', 'server.py'):
            self.send_error(404)
            return
        size = os.path.getsize(path)
        ctype = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        if path.endswith('.srt'):
            ctype = 'text/plain; charset=utf-8'
        start, end, code = 0, size - 1, 200
        m = re.match(r'bytes=(\d*)-(\d*)', self.headers.get('Range', ''))
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                start = int(m.group(1))
                if m.group(2):
                    end = min(int(m.group(2)), size - 1)
            else:
                start = max(0, size - int(m.group(2)))
            if start > end:
                self.send_error(416)
                return
            code = 206
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(end - start + 1))
        if code == 206:
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.end_headers()
        if not body:
            return
        try:
            with open(path, 'rb') as f:
                f.seek(start)
                left = end - start + 1
                while left > 0:
                    b = f.read(min(1 << 20, left))
                    if not b:
                        break
                    self.wfile.write(b)
                    left -= len(b)
        except (ConnectionError, OSError):
            pass

    def log_message(self, *a):
        pass


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f'Serving on http://127.0.0.1:{port}')
    ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
