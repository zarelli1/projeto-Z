def handler(event, context):
    """Health check ultra simples - sem dependências externas"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        },
        'body': '{"status": "OK", "message": "Sistema NPS funcionando!", "timestamp": "2025-01-04"}'
    }