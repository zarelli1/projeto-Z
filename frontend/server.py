#!/usr/bin/env python3
"""
Servidor Flask eficiente para automação universal
Solução robusta com melhor tratamento de erros
"""

# Adiciona o diretório pai ao path para imports
import sys
import os
import json
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Correção de encoding para Windows
from encoding_fix import setup_windows_encoding
setup_windows_encoding()

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import threading
import webbrowser
from datetime import datetime
from dotenv import load_dotenv
import colorama
from colorama import Fore, Style, Back

# Inicialização Windows com colorama
if sys.platform.startswith('win'):
    colorama.init(autoreset=True, convert=True, strip=False)
    print(f"{Fore.GREEN}[OK] Colorama inicializado para Windows{Style.RESET_ALL}")

# Carrega configurações do .env com override
load_dotenv(override=True)
print(f"{Fore.CYAN}[CONFIG] Variáveis de ambiente carregadas{Style.RESET_ALL}")

# Verifica configuração crítica
if not os.getenv('OPENAI_API_KEY'):
    print(f"{Fore.RED}[ERRO] OPENAI_API_KEY não configurada!{Style.RESET_ALL}")
else:
    print(f"{Fore.GREEN}[OK] OpenAI API configurada{Style.RESET_ALL}")

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app, origins=['*'], methods=['GET', 'POST', 'OPTIONS'], allow_headers=['Content-Type'])  # CORS otimizado

# Cache para melhorar performance
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import WSGIRequestHandler
import time
import socket

# Configurações de cache e timeout
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache de 1 ano para arquivos estáticos
WSGIRequestHandler.timeout = 300  # Timeout de 5 minutos para requests longos

# Configurações com variáveis de ambiente
DEFAULT_PORT = 3001  # Porta única padronizada
FALLBACK_PORTS = [3002, 3003, 3004]  # Fallbacks organizados
PORT = int(os.getenv('FLASK_PORT', DEFAULT_PORT))
HOST = os.getenv('FLASK_HOST', '0.0.0.0')
DEBUG = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Timeouts otimizados
TIMEOUTS = {
    'test_endpoint': 30,      # Era 15s
    'full_analysis': 120,     # Era 60s
    'individual_request': 10   # Para requests individuais
}

class ErrorHandler:
    """Tratamento robusto de erros com retry e fallbacks"""
    
    @staticmethod
    def with_retry(func, max_retries=3, delay=1):
        """Executa função com retry e backoff exponencial"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(delay * (2 ** attempt))  # Backoff exponencial
        
    @staticmethod
    def safe_response(data=None, error=None, status=200):
        """Retorna resposta padronizada com tratamento de erro"""
        return {
            'success': error is None,
            'data': data,
            'error': str(error) if error else None,
            'timestamp': datetime.now().isoformat()
        }, status

def find_available_port(preferred_port, fallback_ports):
    """Encontra porta disponeível"""
    def check_port(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return True
            except socket.error:
                return False
    
    # Tenta porta preferida primeiro
    if check_port(preferred_port):
        return preferred_port
    
    # Tenta fallbacks
    for port in fallback_ports:
        if check_port(port):
            return port
    
    # Fallback final
    return preferred_port
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(FRONTEND_DIR)

@app.route('/')
def index():
    """Serve a página principal"""
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve arquivos estáticos"""
    return send_from_directory(FRONTEND_DIR, filename)

@app.route('/relatorios/<path:filename>')
def serve_reports(filename):
    """Serve relatórios"""
    # Usa o mesmo caminho que o gerador_doc.py usa
    base_dir = os.path.dirname(BASE_DIR)  # Volta para a raiz do projeto
    relatorios_dir = os.path.abspath(os.path.join(base_dir, "relatorios"))
    
    print(f"[DEBUG] Base dir: {base_dir}")
    print(f"[DEBUG] Procurando arquivo em: {relatorios_dir}")
    print(f"[DEBUG] Nome do arquivo: {filename}")
    
    arquivo_path = os.path.join(relatorios_dir, filename)
    if os.path.exists(arquivo_path):
        print(f"[DEBUG] Arquivo encontrado: {arquivo_path}")
        try:
            return send_from_directory(relatorios_dir, filename)
        except Exception as e:
            print(f"[ERROR] Erro ao enviar arquivo: {e}")
            return f"Erro ao enviar arquivo: {str(e)}", 500
    else:
        print(f"[DEBUG] Arquivo não encontrado: {arquivo_path}")
        try:
            print("[DEBUG] Listando conteúdo da pasta relatorios:")
            for f in os.listdir(relatorios_dir):
                print(f"  - {f}")
        except Exception as e:
            print(f"[ERROR] Erro ao listar pasta: {e}")
        return "", 404

@app.route('/api/test', methods=['POST'])
def test_extraction():
    """Endpoint de teste rápido para validar URL"""
    try:
        data = request.get_json()
        sheets_url = data.get('sheets_url', '')
        
        if not sheets_url:
            return jsonify({'success': False, 'error': 'URL necessária'})
        
        # Validação básica da URL
        import re
        if not re.match(r'https://docs\.google\.com/spreadsheets/d/[a-zA-Z0-9-_]+', sheets_url):
            return jsonify({'success': False, 'error': 'URL inválida. Use formato: https://docs.google.com/spreadsheets/d/...'})
        
        # Teste rápido de conexão
        import requests
        try:
            # Extrai ID da planilha
            sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheets_url)
            if not sheet_id_match:
                return jsonify({'success': False, 'error': 'ID da planilha não encontrado na URL'})
            
            sheet_id = sheet_id_match.group(1)
            
            # Testa acesso básico com timeout otimizado
            test_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
            response = requests.get(test_url, timeout=TIMEOUTS['test_endpoint'], allow_redirects=True)
            
            if response.status_code == 200 and len(response.text) > 50:
                return jsonify({
                    'success': True,
                    'message': 'Conexão OK! Planilha acessível.',
                    'sheet_id': sheet_id
                })
            else:
                return jsonify({'success': False, 'error': 'Planilha não está pública ou não existe'})
                
        except requests.exceptions.Timeout:
            return jsonify({'success': False, 'error': f'Timeout após {TIMEOUTS["test_endpoint"]}s - planilha demorou muito para responder'})
        except Exception as e:
            return jsonify({'success': False, 'error': f'Erro de conexão: {str(e)}'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde do servidor"""
    return jsonify({
        'status': 'OK',
        'message': 'DashBot funcionando',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_data():
    """Endpoint principal para análise universal - Suporte para upload e URLs"""
    
    if request.method == 'OPTIONS':
        # Resposta para preflight CORS
        return '', 200
    
    try:
        print("[ANALYZE] NOVA REQUISICAO DE ANALISE")
        
        # Verifica se é upload de arquivo ou URL
        if 'file' in request.files:
            # Upload de arquivo CSV
            result = handle_file_upload()
        else:
            # URL do Google Sheets (método original)
            result = handle_sheets_url()
        
        print("[ANALYZE] ANALISE CONCLUIDA")
        return jsonify(result)
        
    except Exception as e:
        print(f"[ERROR] ERRO NA API: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

def handle_file_upload():
    """Processa upload de arquivo CSV"""
    print("[UPLOAD] Processando upload de arquivo...")
    
    file = request.files['file']
    if not file or file.filename == '':
        return {
            'success': False,
            'error': 'Nenhum arquivo selecionado'
        }
    
    # Parâmetros do formulário
    loja_nome = request.form.get('nome_loja', 'Upload Teste')
    usar_looker = request.form.get('usar_looker', 'false').lower() == 'true'
    gerar_ia = request.form.get('gerar_ia', 'false').lower() == 'true'
    estilo_pdf = request.form.get('estilo_pdf', 'moderno')  # NOVO: Estilo do PDF
    
    print(f"[LOJA] Loja: {loja_nome}")
    print(f"[CONFIG] Usar Looker: {usar_looker}")
    print(f"[IA] Gerar IA: {gerar_ia}")
    print(f"[PDF] Estilo PDF: {estilo_pdf}")
    
    # Salva arquivo temporário
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp:
        file.save(tmp.name)
        csv_path = tmp.name
    
    try:
        # Carrega dados do CSV
        import pandas as pd
        dados = pd.read_csv(csv_path, encoding='utf-8')
        print(f"[CSV] {len(dados)} registros carregados do CSV")
        print(f"[COLUMNS] Colunas: {list(dados.columns)}")
        
        # Executar análise inteligente com IA e DOC
        from analisador_ia_simple import AnalisadorIACustomizado
        from gerador_doc import gerar_doc_inteligente as gerar_doc_upload
        
        # Simula dados segmentados para upload CSV (não tem abas específicas)
        dados_segmentados_simulados = {
            'todos': dados,
            'atendimento': dados if any('telefone' in col.lower() for col in dados.columns) else None,
            'produto': dados if any('whatsapp' in col.lower() for col in dados.columns) else None,
            'nps_ruim': dados if any('situacao' in col.lower() for col in dados.columns) else None
        }
        
        print("[IA] Analise inteligente dos dados...")
        analisador_ia = AnalisadorIACustomizado(dados_segmentados_simulados, loja_nome)
        relatorio_ia = analisador_ia.gerar_analise_completa()
        
        if not relatorio_ia:
            return {
                'success': False,
                'error': 'Erro na análise inteligente dos dados.'
            }
        
        # Gerar DOC com gerador seguro
        print("[DOC] Gerando documento...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo_doc = f"analise_pos_venda_{loja_nome.replace(' ', '_')}_{timestamp}.docx"
        
        try:
            caminho_arquivo = gerar_doc_upload(relatorio_ia, loja_nome, nome_arquivo_doc)
            
            if not caminho_arquivo:
                return {
                    'success': False,
                    'error': 'Função gerar_doc_upload retornou None'
                }
        except Exception as e:
            print(f"DEBUG: Erro na geração DOC upload: {str(e)}")
            return {
                'success': False,
                'error': f'Erro na geração do relatório upload: {str(e)}'
            }
        
        import os
        nome_arquivo = os.path.basename(caminho_arquivo)
        
        # Calcular métricas básicas para o frontend
        nps_score = 0
        avg_rating = 0
        vendedores_count = 0
        
        # Tentar extrair métricas básicas dos dados com melhor detecção
        try:
            # Buscar colunas de avaliação com mais variações
            col_avaliacao = None
            for col in dados.columns:
                col_lower = str(col).lower()
                if any(palavra in col_lower for palavra in ['avaliacao', 'avaliação', 'nota', 'score', 'rating']):
                    col_avaliacao = col
                    break
            
            if col_avaliacao:
                # Converter para numérico e filtrar valores válidos
                avaliacoes_serie = pd.to_numeric(dados[col_avaliacao], errors='coerce')
                avaliacoes_validas = avaliacoes_serie.dropna()
                avaliacoes_validas = avaliacoes_validas[(avaliacoes_validas >= 0) & (avaliacoes_validas <= 10)]
                
                if len(avaliacoes_validas) > 0:
                    avg_rating = float(avaliacoes_validas.mean())
                    promotores = len(avaliacoes_validas[avaliacoes_validas >= 9])
                    detratores = len(avaliacoes_validas[avaliacoes_validas <= 6])
                    nps_score = ((promotores - detratores) / len(avaliacoes_validas)) * 100
                    print(f"[METRICS] Metricas calculadas: NPS={nps_score:.1f}, Media={avg_rating:.1f}")
            
            # Contar vendedores únicos com melhor detecção
            col_vendedor = None
            for col in dados.columns:
                col_lower = str(col).lower()
                if any(palavra in col_lower for palavra in ['vendedor', 'atendente', 'consultor', 'funcionario']):
                    col_vendedor = col
                    break
            
            if col_vendedor:
                vendedores_unicos = dados[col_vendedor].dropna().nunique()
                vendedores_count = int(vendedores_unicos)
                print(f"[VENDEDORES] Vendedores unicos encontrados: {vendedores_count}")
                
        except Exception as e:
            print(f"[WARNING] Erro ao calcular metricas basicas: {e}")
            # Garantir valores padrão em caso de erro
            nps_score = 0
            avg_rating = 0
            vendedores_count = 0

        result = {
            'success': True,
            'message': 'Análise concluída com sucesso! Documento profissional gerado.',
            'arquivo': nome_arquivo,
            'download_url': f'/relatorios/{nome_arquivo}',
            'dados': {
                'total_registros': len(dados),
                'nps_score': round(nps_score, 1),
                'avg_rating': round(avg_rating, 1),
                'vendedores': vendedores_count,
                'loja_nome': loja_nome
            },
            'tipo_relatorio': 'Análise NPS - Documento DOC'
        }
        
        # Remove arquivo temporário
        os.unlink(csv_path)
        
        return result
        
    except Exception as e:
        # Remove arquivo temporário em caso de erro
        if os.path.exists(csv_path):
            os.unlink(csv_path)
        raise e

def handle_sheets_url():
    """Processa URL do Google Sheets (método original)"""
    print("[URL] Processando URL do Google Sheets...")
    
    data = request.get_json()
    if not data:
        return {
            'success': False,
            'error': 'Dados não fornecidos'
        }
    
    sheets_url = data.get('sheets_url', '')
    loja_nome = data.get('loja_nome', 'Análise Universal')
    estilo_pdf = data.get('estilo_pdf', 'mdo_weasy')  # Novo parâmetro
    data_inicio = data.get('data_inicio')  # NOVO: Filtro por data início
    data_fim = data.get('data_fim')  # NOVO: Filtro por data fim
    
    print(f"[URL] URL: {sheets_url}")
    print(f"[LOJA] Projeto: {loja_nome}")
    print(f"[PDF] Estilo PDF: {estilo_pdf}")
    
    # Exibe informações sobre filtro por data se aplicável
    if data_inicio or data_fim:
        print("[DATA] Filtro por data solicitado:")
        if data_inicio:
            print(f"   [DATA] Data início: {data_inicio}")
        if data_fim:
            print(f"   [DATA] Data fim: {data_fim}")
    
    if not sheets_url:
        return {
            'success': False,
            'error': 'URL da planilha é obrigatória'
        }
    
    # Executa análise original com filtro por data
    return run_analysis(sheets_url, loja_nome, estilo_pdf, data_inicio, data_fim)

def run_analysis(sheets_url, loja_nome, estilo_pdf='mdo_weasy', data_inicio=None, data_fim=None):
    """Executa análise e gera PDF MDO com emojis reais"""
    try:
        print(f"INICIANDO ANÁLISE MDO para: {loja_nome}")
        
        # Importa sistema integrado
        print("DEBUG: Importando módulos...")
        from analisador_nps_completo import AnalisadorNPSCompleto
        from analisador_ia_simple import AnalisadorIACustomizado
        from gerador_doc import gerar_doc_inteligente
        from adaptador_dados import AdaptadorDados
        print("DEBUG: Módulos importados com sucesso")
        
        # 1. EXTRAÇÃO COM NOVO SISTEMA IA (COM FILTRO POR DATA)
        print("[EXTRACT] PASSO 1: Extraindo dados com IA avancada...")
        analisador_completo = AnalisadorNPSCompleto(loja_nome)
        
        if not analisador_completo._extrair_abas_automaticamente(sheets_url):
            return {
                'success': False,
                'error': 'Não foi possível conectar com a planilha. Verifique se está pública.'
            }
        
        # Padroniza dados automaticamente
        analisador_completo._padronizar_todos_dados()
        
        # Aplica filtro por data se especificado
        if data_inicio or data_fim:
            print("[DATA] Aplicando filtro por data...")
            analisador_completo._aplicar_filtro_data(data_inicio, data_fim)
        
        # Converte para formato compatível
        adaptador = AdaptadorDados()
        dados_segmentados = adaptador.converter_para_formato_antigo(analisador_completo.dados_abas, data_inicio, data_fim)
        
        if not dados_segmentados or dados_segmentados.get('todos') is None or len(dados_segmentados.get('todos', [])) == 0:
            return {
                'success': False,
                'error': 'Nenhum dado encontrado. O sistema adaptativo analisou todas as abas mas não encontrou estrutura reconhecível com colunas de avaliação/feedback.'
            }
        
        dados = dados_segmentados['todos']
        
        # Informa sobre os tipos detectados
        tipos_detectados = []
        for tipo, dados_tipo in dados_segmentados.items():
            if dados_tipo is not None and tipo != 'todos':
                tipos_detectados.append(tipo)
        
        if tipos_detectados:
            print(f"[DETECT] Sistema adaptativo detectou: {', '.join(tipos_detectados)}")
        
        print(f"[OK] {len(dados)} registros extraidos com sistema adaptativo")
        
        # 2. ANÁLISE INTELIGENTE COM IA
        print("[IA] PASSO 2: Analise inteligente dos dados...")
        
        analisador_ia = AnalisadorIACustomizado(dados_segmentados, loja_nome)
        relatorio_ia = analisador_ia.gerar_analise_completa()
        
        if not relatorio_ia:
            return {
                'success': False,
                'error': 'Erro na análise inteligente dos dados.'
            }
        
        # 3. GERAÇÃO DO DOCUMENTO COM GERADOR SEGURO
        print("[DOC] PASSO 3: Gerando documento...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo_doc = f"analise_pos_venda_{loja_nome.replace(' ', '_')}_{timestamp}.docx"
        
        try:
            caminho_arquivo = gerar_doc_inteligente(relatorio_ia, loja_nome, nome_arquivo_doc)
            print(f"DEBUG: caminho_arquivo retornado = {caminho_arquivo}")
            
            if not caminho_arquivo:
                return {
                    'success': False,
                    'error': 'Função gerar_doc_inteligente retornou None'
                }
        except Exception as e:
            print(f"DEBUG: Erro na geração DOC: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'Erro na geração do relatório: {str(e)}'
            }
        
        # Extrair apenas o nome do arquivo
        nome_arquivo = os.path.basename(caminho_arquivo)
        
        print(f"[OK] Documento DOC gerado: {nome_arquivo}")
        
        # Calcular métricas básicas para o frontend
        nps_score = 0
        avg_rating = 0
        vendedores_count = 0
        
        # Tentar extrair métricas básicas dos dados com melhor detecção
        try:
            # Buscar colunas de avaliação com mais variações
            col_avaliacao = None
            for col in dados.columns:
                col_lower = str(col).lower()
                if any(palavra in col_lower for palavra in ['avaliacao', 'avaliação', 'nota', 'score', 'rating']):
                    col_avaliacao = col
                    break
            
            if col_avaliacao:
                # Converter para numérico e filtrar valores válidos
                avaliacoes_serie = pd.to_numeric(dados[col_avaliacao], errors='coerce')
                avaliacoes_validas = avaliacoes_serie.dropna()
                avaliacoes_validas = avaliacoes_validas[(avaliacoes_validas >= 0) & (avaliacoes_validas <= 10)]
                
                if len(avaliacoes_validas) > 0:
                    avg_rating = float(avaliacoes_validas.mean())
                    promotores = len(avaliacoes_validas[avaliacoes_validas >= 9])
                    detratores = len(avaliacoes_validas[avaliacoes_validas <= 6])
                    nps_score = ((promotores - detratores) / len(avaliacoes_validas)) * 100
                    print(f"[METRICS] Metricas calculadas: NPS={nps_score:.1f}, Media={avg_rating:.1f}")
            
            # Contar vendedores únicos com melhor detecção
            col_vendedor = None
            for col in dados.columns:
                col_lower = str(col).lower()
                if any(palavra in col_lower for palavra in ['vendedor', 'atendente', 'consultor', 'funcionario']):
                    col_vendedor = col
                    break
            
            if col_vendedor:
                vendedores_unicos = dados[col_vendedor].dropna().nunique()
                vendedores_count = int(vendedores_unicos)
                print(f"[VENDEDORES] Vendedores unicos encontrados: {vendedores_count}")
                
        except Exception as e:
            print(f"[WARNING] Erro ao calcular metricas basicas: {e}")
            # Garantir valores padrão em caso de erro
            nps_score = 0
            avg_rating = 0
            vendedores_count = 0
        
        # Retornar estrutura compatível com frontend
        return {
            'success': True,
            'message': 'Análise concluída com sucesso! Documento profissional gerado.',
            'arquivo': nome_arquivo,
            'download_url': f'/relatorios/{nome_arquivo}',
            'dados': {
                'total_registros': len(dados),
                'nps_score': round(nps_score, 1),
                'avg_rating': round(avg_rating, 1),
                'vendedores': vendedores_count,
                'loja_nome': loja_nome
            },
            'tipo_relatorio': 'Análise NPS - Documento DOC'
        }
        
    except Exception as e:
        print(f"[ERROR] ERRO NA ANALISE MDO: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'success': False,
            'error': f'Erro ao gerar análise MDO: {str(e)}'
        }


def start_server():
    """Inicia o servidor Flask com detecção automática de porta"""
    global PORT
    
    # Encontra porta disponível
    available_port = find_available_port(PORT, FALLBACK_PORTS)
    if available_port != PORT:
        print(f"[AVISO] Porta {PORT} ocupada, usando {available_port}")
        PORT = available_port
    
    print(f"{Fore.CYAN}DASHBOT - SERVIDOR FLASK{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=" * 60 + f"{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Rodando em: http://localhost:{PORT}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}IA: GPT-4o integrada{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Suporte: Qualquer planilha{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}API: /api/analyze{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Timeouts: Test {TIMEOUTS['test_endpoint']}s | Analysis {TIMEOUTS['full_analysis']}s{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=" * 60 + f"{Style.RESET_ALL}")
    print(f"{Fore.RED}Ctrl+C para parar{Style.RESET_ALL}")
    print()
    
    # Abre navegador em thread separada
    def open_browser():
        import time
        time.sleep(1)  # Aguarda servidor iniciar
        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except:
            print(f"Abra manualmente: http://localhost:{PORT}")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Inicia servidor Flask com configurações otimizadas
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)

if __name__ == "__main__":
    start_server()