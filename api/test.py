import json
import re

def handler(request):
    """
    CORREÇÃO: Test connection endpoint com tratamento robusto de request
    Formato compatível com Vercel serverless functions
    """
    
    try:
        # Handle CORS preflight
        method = getattr(request, 'method', 'POST')
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
    
        # CORREÇÃO: Parse request body com múltiplos fallbacks
        data = {}
        try:
            if hasattr(request, 'get_json') and callable(request.get_json):
                data = request.get_json() or {}
            elif hasattr(request, 'json') and callable(request.json):
                data = request.json() or {}
            elif hasattr(request, 'body'):
                body_content = request.body
                if isinstance(body_content, bytes):
                    body_content = body_content.decode('utf-8')
                if body_content:
                    data = json.loads(body_content)
            elif hasattr(request, 'data'):
                if request.data:
                    data = json.loads(request.data)
        except (json.JSONDecodeError, AttributeError, TypeError) as parse_error:
            # CORREÇÃO: Se não conseguir fazer parse, retorna erro claro
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({'success': False, 'error': f'JSON inválido: {str(parse_error)}'})
            }
        
        sheets_url = data.get('sheets_url', '')
        
        if not sheets_url:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({'success': False, 'error': 'URL necessária'})
            }
        
        # Validação básica da URL
        if not re.match(r'https://docs\.google\.com/spreadsheets/d/[a-zA-Z0-9-_]+', sheets_url):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({'success': False, 'error': 'URL inválida. Use formato do Google Sheets'})
            }
        
        # Extrai ID da planilha
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheets_url)
        if not sheet_id_match:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({'success': False, 'error': 'ID da planilha não encontrado'})
            }
        
        sheet_id = sheet_id_match.group(1)
        
        # Testa acesso básico SEM requests (para evitar dependências)
        try:
            import urllib.request
            import urllib.error
            
            test_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
            
            try:
                with urllib.request.urlopen(test_url, timeout=10) as response:
                    content = response.read().decode('utf-8')
                    
                    if response.status == 200 and len(content) > 50:
                        return {
                            'statusCode': 200,
                            'headers': {
                                'Content-Type': 'application/json',
                                'Access-Control-Allow-Origin': '*',
                            },
                            'body': json.dumps({
                                'success': True,
                                'message': 'Conexão OK! Planilha acessível.',
                                'sheet_id': sheet_id
                            })
                        }
                    else:
                        return {
                            'statusCode': 400,
                            'headers': {
                                'Content-Type': 'application/json',
                                'Access-Control-Allow-Origin': '*',
                            },
                            'body': json.dumps({'success': False, 'error': 'Planilha não está pública'})
                        }
                        
            except urllib.error.URLError:
                return {
                    'statusCode': 408,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    'body': json.dumps({'success': False, 'error': 'Timeout - planilha demorou para responder'})
                }
                
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({'success': False, 'error': f'Erro de conexão: {str(e)}'})
            }
            
    except Exception as e:
        # CORREÇÃO: Tratamento de erro final com logging detalhado
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'success': False, 
                'error': f'Erro interno do servidor: {str(e)}',
                'type': 'server_error'
            })
        }