import json
from datetime import datetime

def handler(request, context):
    """Vercel serverless function para health check"""
    
    # Handle CORS
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
        },
        'body': json.dumps({
            'status': 'OK',
            'message': 'DashBot funcionando no Vercel',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0-vercel'
        })
    }