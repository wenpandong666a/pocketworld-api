"""ACLED 冲突数据 API 代理 - Vercel Serverless Function"""
import json
import time
from urllib.request import Request, urlopen
from urllib.parse import urlencode

# ===== 配置 (替换为你的 ACLED 账号) =====
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

def handler(req):
    """Vercel Python Serverless Function 入口"""
    params = dict(req.args)
    params['email'] = ACLED_EMAIL
    params['key'] = ACLED_API_KEY
    
    cache_key = json.dumps(params, sort_keys=True)
    cached = _cache_get(cache_key)
    if cached:
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(cached)
        }
    
    query_string = urlencode(params)
    full_url = f'{ACLED_URL}?{query_string}'
    
    request = Request(full_url)
    request.add_header('User-Agent', 'Mozilla/5.0')
    
    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            _cache_set(cache_key, data)
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(data)
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
