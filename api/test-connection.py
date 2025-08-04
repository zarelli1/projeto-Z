from http.server import BaseHTTPRequestHandler
import json
import re
import requests

class handler(BaseHTTPRequestHandler):
    """Teste de conexão com Google Sheets - versão simplificada"""
    
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
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
        body = event.get('body', '{}')
        if isinstance(body, str):
            data = json.loads(body) if body else {}
        else:
            data = body
        
        sheets_url = data.get('sheets_url', '')
        
        if not sheets_url:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({'success': False, 'error': 'URL da planilha é obrigatória'})
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
        
        # Testa acesso básico
        import requests
        test_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
        
        try:
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200 and len(response.text) > 50:
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
                
        except requests.exceptions.Timeout:
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
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({'success': False, 'error': f'Erro interno: {str(e)}'})
        }