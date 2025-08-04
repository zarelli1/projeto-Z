def handler(request):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': '{"message": "API funcionando!", "status": "OK"}'
    }