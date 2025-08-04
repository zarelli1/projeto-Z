from http.server import BaseHTTPRequestHandler
import json
import re
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
            
            sheets_url = data.get('sheets_url', '')
            
            if not sheets_url:
                self.send_error_response(400, {'success': False, 'error': 'URL necessária'})
                return
            
            # Validação básica da URL
            if not re.match(r'https://docs\.google\.com/spreadsheets/d/[a-zA-Z0-9-_]+', sheets_url):
                self.send_error_response(400, {'success': False, 'error': 'URL inválida. Use formato do Google Sheets'})
                return
            
            # Extrai ID da planilha
            sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheets_url)
            if not sheet_id_match:
                self.send_error_response(400, {'success': False, 'error': 'ID da planilha não encontrado'})
                return
            
            sheet_id = sheet_id_match.group(1)
            
            # Testa acesso básico
            test_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200 and len(response.text) > 50:
                self.send_success_response({
                    'success': True,
                    'message': 'Conexão OK! Planilha acessível.',
                    'sheet_id': sheet_id
                })
            else:
                self.send_error_response(400, {'success': False, 'error': 'Planilha não está pública'})
                
        except requests.exceptions.Timeout:
            self.send_error_response(408, {'success': False, 'error': 'Timeout - planilha demorou para responder'})
        except Exception as e:
            self.send_error_response(500, {'success': False, 'error': f'Erro interno: {str(e)}'})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_success_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_error_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())