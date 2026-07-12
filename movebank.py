"""Movebank API 代理 - Vercel Serverless Function
处理 Basic Auth + 许可协议 MD5 + 数据缓存
"""
import hashlib
import json
import time
from http.server import HTTPServer
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

def handler(req):
    """Vercel Python Serverless Function 入口"""
    # 解析查询参数
    params = dict(req.args)
    
    if not params:
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'status': 'ok', 'service': 'movebank'})
        }
    
    cache_key = json.dumps(params, sort_keys=True)
    ttl = 86400 if params.get('entity_type') == 'event' else 3600
    cached = _cache_get(cache_key, ttl)
    if cached:
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'text/csv'
            },
            'body': cached
        }
    
    # 构建 Movebank API URL
    import urllib.parse
    import base64
    
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
                    return {
                        'statusCode': 403,
                        'headers': {'Access-Control-Allow-Origin': '*'},
                        'body': 'License agreement required'
                    }
            
            _cache_set(cache_key, content)
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'text/csv'
                },
                'body': content
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': str(e)
        }
