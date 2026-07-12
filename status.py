"""状态检查端点"""
import json

def handler(req):
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'status': 'ok',
            'services': {'movebank': True, 'acled': True}
        })
    }
