#!/usr/bin/env python3
"""
Servidor Flask eficiente para automação universal
Solução robusta com melhor tratamento de erros
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import json
import threading
import webbrowser
from datetime import datetime

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)  # Permite CORS para todas as rotas

# Configurações
PORT = 8080
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
    """Serve relatórios PDF"""
    relatorios_dir = os.path.join(BASE_DIR, 'relatorios')
    return send_from_directory(relatorios_dir, filename)

@app.route('/api/test', methods=['POST'])
def test_extraction():
    """Endpoint de teste para debug"""
    try:
        data = request.get_json()
        sheets_url = data.get('sheets_url', '')
        
        if not sheets_url:
            return jsonify({'success': False, 'error': 'URL necessária'})
        
        # Teste com novo sistema
        from analisador_nps_completo import AnalisadorNPSCompleto
        analisador = AnalisadorNPSCompleto()
        
        if analisador._extrair_abas_automaticamente(sheets_url):
            analisador._padronizar_todos_dados()
            
            total_registros = sum(len(df) for df in analisador.dados_abas.values() if df is not None)
            abas_encontradas = list(analisador.dados_abas.keys())
            
            return jsonify({
                'success': True,
                'registros': total_registros,
                'abas_encontradas': abas_encontradas,
                'detalhes': {aba: len(df) for aba, df in analisador.dados_abas.items() if df is not None}
            })
        else:
            return jsonify({'success': False, 'error': 'Falha na conexão'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_data():
    """Endpoint principal para análise universal - Suporte para upload e URLs"""
    
    if request.method == 'OPTIONS':
        # Resposta para preflight CORS
        return '', 200
    
    try:
        print("📨 NOVA REQUISIÇÃO DE ANÁLISE")
        
        # Verifica se é upload de arquivo ou URL
        if 'file' in request.files:
            # Upload de arquivo CSV
            result = handle_file_upload()
        else:
            # URL do Google Sheets (método original)
            result = handle_sheets_url()
        
        print("✅ ANÁLISE CONCLUÍDA")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ ERRO NA API: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

def handle_file_upload():
    """Processa upload de arquivo CSV"""
    print("📤 Processando upload de arquivo...")
    
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
    
    print(f"🏢 Loja: {loja_nome}")
    print(f"📊 Usar Looker: {usar_looker}")
    print(f"🤖 Gerar IA: {gerar_ia}")
    print(f"🎨 Estilo PDF: {estilo_pdf}")
    
    # Salva arquivo temporário
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp:
        file.save(tmp.name)
        csv_path = tmp.name
    
    try:
        # Carrega dados do CSV
        import pandas as pd
        dados = pd.read_csv(csv_path, encoding='utf-8')
        print(f"✅ {len(dados)} registros carregados do CSV")
        print(f"📋 Colunas: {list(dados.columns)}")
        
        # Executar análise inteligente com IA e PDF MDO
        from analisador_ia_simple import AnalisadorIACustomizado
        from gerador_pdf import GeradorPDFCustomizado
        
        # Simula dados segmentados para upload CSV (não tem abas específicas)
        dados_segmentados_simulados = {
            'todos': dados,
            'atendimento': dados if any('telefone' in col.lower() for col in dados.columns) else None,
            'produto': dados if any('whatsapp' in col.lower() for col in dados.columns) else None,
            'nps_ruim': dados if any('situacao' in col.lower() for col in dados.columns) else None
        }
        
        print("🤖 Análise inteligente dos dados...")
        analisador_ia = AnalisadorIACustomizado(dados_segmentados_simulados, loja_nome)
        relatorio_ia = analisador_ia.gerar_analise_completa()
        
        if not relatorio_ia:
            return {
                'success': False,
                'error': 'Erro na análise inteligente dos dados.'
            }
        
        # Gerar PDF MDO com WeasyPrint e emojis nativos
        print("📄 Gerando PDF MDO com WeasyPrint e emojis nativos...")
        gerador = GeradorPDFCustomizado()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo_pdf = f"analise_pos_venda_{loja_nome.replace(' ', '_')}_{timestamp}.pdf"
        
        # Garante que o arquivo seja salvo no diretório relatorios
        relatorios_dir = os.path.join(BASE_DIR, 'relatorios')
        os.makedirs(relatorios_dir, exist_ok=True)
        
        caminho_completo = os.path.join(relatorios_dir, nome_arquivo_pdf)
        caminho_arquivo = gerador.gerar_pdf_customizado(relatorio_ia, loja_nome, caminho_completo)
        
        if not caminho_arquivo:
            return {
                'success': False,
                'error': 'Erro ao gerar relatório PDF.'
            }
        
        import os
        nome_arquivo = os.path.basename(caminho_arquivo)
        
        result = {
            'success': True,
            'message': 'Análise MDO concluída com sucesso! PDF profissional gerado com WeasyPrint.',
            'arquivo': nome_arquivo,
            'download_url': f'/relatorios/{nome_arquivo}',
            'dados': {
                'total_registros': len(dados),
                'loja_nome': loja_nome
            },
            'tipo_relatorio': 'Análise MDO - WeasyPrint'
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
    print("🔗 Processando URL do Google Sheets...")
    
    data = request.get_json()
    if not data:
        return {
            'success': False,
            'error': 'Dados não fornecidos'
        }
    
    sheets_url = data.get('sheets_url', '')
    loja_nome = data.get('loja_nome', 'Análise Universal')
    estilo_pdf = data.get('estilo_pdf', 'mdo_weasy')  # Novo parâmetro
    
    print(f"🔗 URL: {sheets_url}")
    print(f"🏢 Projeto: {loja_nome}")
    print(f"🎨 Estilo PDF: {estilo_pdf}")
    
    if not sheets_url:
        return {
            'success': False,
            'error': 'URL da planilha é obrigatória'
        }
    
    # Executa análise original
    return run_analysis(sheets_url, loja_nome, estilo_pdf)

def run_analysis(sheets_url, loja_nome, estilo_pdf='mdo_weasy'):
    """Executa análise e gera PDF MDO com emojis reais"""
    try:
        print(f"📊 INICIANDO ANÁLISE MDO para: {loja_nome}")
        
        # Importa sistema integrado
        from analisador_nps_completo import AnalisadorNPSCompleto
        from analisador_ia_simple import AnalisadorIACustomizado
        from gerador_pdf import GeradorPDFCustomizado
        from adaptador_dados import AdaptadorDados
        
        # 1. EXTRAÇÃO COM NOVO SISTEMA IA
        print("🔍 PASSO 1: Extraindo dados com IA avançada...")
        analisador_completo = AnalisadorNPSCompleto(loja_nome)
        
        if not analisador_completo._extrair_abas_automaticamente(sheets_url):
            return {
                'success': False,
                'error': 'Não foi possível conectar com a planilha. Verifique se está pública.'
            }
        
        # Padroniza dados automaticamente
        analisador_completo._padronizar_todos_dados()
        
        # Converte para formato compatível
        adaptador = AdaptadorDados()
        dados_segmentados = adaptador.converter_para_formato_antigo(analisador_completo.dados_abas)
        
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
            print(f"🎯 Sistema adaptativo detectou: {', '.join(tipos_detectados)}")
        
        print(f"✅ {len(dados)} registros extraídos com sistema adaptativo")
        
        # 2. ANÁLISE INTELIGENTE COM IA
        print("🤖 PASSO 2: Análise inteligente dos dados...")
        
        analisador_ia = AnalisadorIACustomizado(dados_segmentados, loja_nome)
        relatorio_ia = analisador_ia.gerar_analise_completa()
        
        if not relatorio_ia:
            return {
                'success': False,
                'error': 'Erro na análise inteligente dos dados.'
            }
        
        # 3. GERAÇÃO DO PDF MDO COM WEASYPRINT
        print("📄 PASSO 3: Gerando PDF MDO com WeasyPrint...")
        
        gerador = GeradorPDFCustomizado()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo_pdf = f"analise_pos_venda_{loja_nome.replace(' ', '_')}_{timestamp}.pdf"
        
        # Garante que o arquivo seja salvo no diretório relatorios
        relatorios_dir = os.path.join(BASE_DIR, 'relatorios')
        os.makedirs(relatorios_dir, exist_ok=True)
        
        caminho_completo = os.path.join(relatorios_dir, nome_arquivo_pdf)
        caminho_arquivo = gerador.gerar_pdf_customizado(relatorio_ia, loja_nome, caminho_completo)
        
        if not caminho_arquivo:
            return {
                'success': False,
                'error': 'Erro ao gerar relatório PDF.'
            }
        
        # Extrair apenas o nome do arquivo
        nome_arquivo = os.path.basename(caminho_arquivo)
        
        print(f"✅ PDF MDO gerado: {nome_arquivo}")
        
        # Retornar estrutura compatível com frontend
        return {
            'success': True,
            'message': 'Análise MDO concluída com sucesso! PDF profissional gerado com WeasyPrint.',
            'arquivo': nome_arquivo,
            'download_url': f'/relatorios/{nome_arquivo}',
            'dados': {
                'total_registros': len(dados),
                'loja_nome': loja_nome
            },
            'tipo_relatorio': 'Análise MDO - WeasyPrint'
        }
        
    except Exception as e:
        print(f"❌ ERRO NA ANÁLISE MDO: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'success': False,
            'error': f'Erro ao gerar análise MDO: {str(e)}'
        }


def start_server():
    """Inicia o servidor Flask"""
    print("🚀 SOCIALZAP UNIVERSAL - SERVIDOR FLASK")
    print("=" * 60)
    print(f"📡 Rodando em: http://localhost:{PORT}")
    print(f"🧠 IA: GPT-4o integrada")
    print(f"📊 Suporte: Qualquer planilha")
    print(f"🔗 API: /api/analyze")
    print("=" * 60)
    print("💡 Ctrl+C para parar")
    print()
    
    # Abre navegador em thread separada
    def open_browser():
        import time
        time.sleep(1)  # Aguarda servidor iniciar
        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except:
            print("🌐 Abra manualmente: http://localhost:8080")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Inicia servidor Flask
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)

if __name__ == "__main__":
    start_server()