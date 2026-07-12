"""ACLED 冲突数据 API 代理 - Vercel Serverless Function"""
from http.server import BaseHTTPRequestHandler
import json, time
from urllib.request import Request, urlopen
from urllib.parse import urlencode, urlparse, parse_qsl

ACLED_EMAIL = 'dove933@163.com'
ACLED_API_KEY = 'mFfSfHdEJ3XGqRtBvWxYz!2'
ACLED_URL = 'https://api.acleddata.com/acled/read'
_cache = {}

def _cache_get(key, ttl=7200):
    if key in _cache:
        entry = _cache[key]
        if time.time() - entry['time'] < ttl:
            return entry['data']
        del _cache[key]
    return None

def _cache_set(key, data):
    _cache[key] = {'data': data, 'time': time.time()}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        parsed = urlparse(self.path)
        params = dict(parse_qsl(parsed.query))
        params['email'] = ACLED_EMAIL
        params['key'] = ACLED_API_KEY
        cache_key = json.dumps(params, sort_keys=True)
        cached = _cache_get(cache_key)
        if cached:
            self.wfile.write(json.dumps(cached).encode())
            return
        query_string = urlencode(params)
        full_url = f'{ACLED_URL}?{query_string}'
        request = Request(full_url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        try:
            with urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                _cache_set(cache_key, data)
                self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
