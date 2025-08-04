def handler(request):
    # Aceita qualquer método HTTP
    if hasattr(request, 'method'):
        method = request.method
    else:
        method = 'UNKNOWN'
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        },
        'body': f'{{"success": true, "message": "Test OK", "method": "{method}"}}'
    }