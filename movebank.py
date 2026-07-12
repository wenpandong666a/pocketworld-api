"""Movebank API 代理 - Vercel Serverless Function
处理 Basic Auth + 许可协议 MD5 + 数据缓存
"""
from http.server import BaseHTTPRequestHandler
import hashlib
import json
import time
import base64
import urllib.parse
from urllib.request import Request, urlopen

# ===== 配置 (替换为你的 Movebank 账号) =====
MB_USER = '13220405736'
MB_PASS = 'wpd20040507'
MB_API = 'https://www.movebank.org/movebank/service/direct-read'

# 简单内存缓存 (Vercel Serverless 实例级别)
_cache = {}

def _cache_get(key, ttl=3600):
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
        
        # 解析查询参数
        parsed = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parsed.query))
        
        if not params:
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'service': 'movebank'}).encode())
            return
        
        self.send_header('Content-Type', 'text/csv')
        self.end_headers()
        
        cache_key = json.dumps(params, sort_keys=True)
        ttl = 86400 if params.get('entity_type') == 'event' else 3600
        cached = _cache_get(cache_key, ttl)
        if cached:
            self.wfile.write(cached.encode())
            return
        
        # 构建 Movebank API URL
        query_string = '&'.join([f'{k}={urllib.parse.quote(str(v))}' for k, v in params.items()])
        api_url = f'{MB_API}?{query_string}'
        
        # 带 Basic Auth 的请求
        auth_header = base64.b64encode(f'{MB_USER}:{MB_PASS}'.encode()).decode()
        
        request = Request(api_url)
        request.add_header('Authorization', f'Basic {auth_header}')
        request.add_header('User-Agent', 'Mozilla/5.0')
        
        try:
            with urlopen(request, timeout=120) as response:
                content = response.read().decode('utf-8')
                
                # 检查是否为许可协议页面
                if 'license-term' in content.lower():
                    md5_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                    # 带许可协议 MD5 重新请求
                    license_params = dict(params)
                    license_params['license-md5'] = md5_hash
                    query_string2 = '&'.join([f'{k}={urllib.parse.quote(str(v))}' for k, v in license_params.items()])
                    api_url2 = f'{MB_API}?{query_string2}'
                    request2 = Request(api_url2)
                    request2.add_header('Authorization', f'Basic {auth_header}')
                    request2.add_header('User-Agent', 'Mozilla/5.0')
                    with urlopen(request2, timeout=120) as response2:
                        content = response2.read().decode('utf-8')
                    
                    if 'license-term' in content.lower():
                        self.wfile.write('License agreement required'.encode())
                        return
                
                _cache_set(cache_key, content)
                self.wfile.write(content.encode())
        except Exception as e:
            self.wfile.write(str(e).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
