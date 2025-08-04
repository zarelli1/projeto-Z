import json

def handler(request):
    """
    CORREÇÃO: Health check endpoint com tratamento robusto de erros
    Formato compatível com Vercel serverless functions
    """
    
    try:
        # Handle CORS preflight
        method = getattr(request, 'method', 'GET')
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
                'body': ''
            }
        
        # CORREÇÃO: JSON response properly formatted com json.dumps()
        response_data = {
            'status': 'OK',
            'message': 'Sistema NPS funcionando!',
            'version': '1.0'
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        # CORREÇÃO: Tratamento de erro que sempre retorna JSON válido
        error_response = {
            'status': 'ERROR',
            'message': f'Erro interno do servidor: {str(e)}'
        }
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(error_response)
        }