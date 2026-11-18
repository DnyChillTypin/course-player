import os, sys, mimetypes, urllib.parse, re
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # needed under `python -I`
import build
COURSES = os.path.join(HERE, 'courses')
GEN = os.path.join(HERE, '.generated')
STATIC = {'/': 'index.html', '/index.html': 'index.html'}


class H(SimpleHTTPRequestHandler):
    def resolve(self):
        p = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
        if p in STATIC:
            return os.path.join(HERE, STATIC[p])
        if p == '/api/rescan':
            build.build()
            return os.path.join(GEN, 'courses.json')
        for prefix, base in (('/media/', COURSES), ('/data/', GEN)):
            if p.startswith(prefix):
                full = os.path.normpath(os.path.join(base, p[len(prefix):]))
                if full.startswith(os.path.normpath(base) + os.sep):
                    return full
        return None

    def do_GET(self):
        self.serve(True)

    def do_HEAD(self):
        self.serve(False)

    def serve(self, body):
        path = self.resolve()
        if not path or not os.path.isfile(path):
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
        if path.startswith(GEN):
            self.send_header('Cache-Control', 'no-store')
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
    os.makedirs(COURSES, exist_ok=True)
    found = build.build()
    print(f'Found {len(found)} course(s): ' + ', '.join(c['slug'] for c in found))
    print(f'Serving on http://127.0.0.1:{port}  (drop new courses into courses/ and refresh the library)')
    ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
