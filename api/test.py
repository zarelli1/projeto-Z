import json
import re
import requests

def handler(request):
    """Vercel serverless function para teste de conexão"""
    
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
    
    try:
        # Parse request body
        if hasattr(request, 'get_json'):
            data = request.get_json()
        else:
            data = json.loads(request.body) if request.body else {}
        
        sheets_url = data.get('sheets_url', '')
        
        if not sheets_url:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({'success': False, 'error': 'URL necessária'})
            }
        
        # Validação básica da URL
        if not re.match(r'https://docs\.google\.com/spreadsheets/d/[a-zA-Z0-9-_]+', sheets_url):
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({'success': False, 'error': 'URL inválida. Use formato: https://docs.google.com/spreadsheets/d/...'})
            }
        
        # Teste rápido de conexão
        try:
            # Extrai ID da planilha
            sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheets_url)
            if not sheet_id_match:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Content-Type': 'application/json',
                    },
                    'body': json.dumps({'success': False, 'error': 'ID da planilha não encontrado na URL'})
                }
            
            sheet_id = sheet_id_match.group(1)
            
            # Testa acesso básico
            test_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
            response = requests.get(test_url, timeout=30, allow_redirects=True)
            
            if response.status_code == 200 and len(response.text) > 50:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Content-Type': 'application/json',
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
                        'Access-Control-Allow-Origin': '*',
                        'Content-Type': 'application/json',
                    },
                    'body': json.dumps({'success': False, 'error': 'Planilha não está pública ou não existe'})
                }
                
        except requests.exceptions.Timeout:
            return {
                'statusCode': 408,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({'success': False, 'error': 'Timeout após 30s - planilha demorou muito para responder'})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({'success': False, 'error': f'Erro de conexão: {str(e)}'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json',
            },
            'body': json.dumps({'success': False, 'error': f'Erro interno: {str(e)}'})
        }