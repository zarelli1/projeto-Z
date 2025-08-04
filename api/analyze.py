import sys
import os
import json
import pandas as pd
from datetime import datetime

# Adiciona o diretório raiz ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Correção de encoding para Windows
try:
    from encoding_fix import setup_windows_encoding
    setup_windows_encoding()
except ImportError:
    pass

def handler(request, context):
    """Vercel serverless function para análise de dados"""
    
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
        loja_nome = data.get('loja_nome', 'Análise Universal')
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')
        
        if not sheets_url:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    'success': False,
                    'error': 'URL da planilha é obrigatória'
                })
            }
        
        # Importa sistema integrado
        from analisador_nps_completo import AnalisadorNPSCompleto
        from analisador_ia_simple import AnalisadorIACustomizado
        from gerador_doc import gerar_doc_inteligente
        from adaptador_dados import AdaptadorDados
        
        # 1. EXTRAÇÃO DE DADOS
        analisador_completo = AnalisadorNPSCompleto(loja_nome)
        
        if not analisador_completo._extrair_abas_automaticamente(sheets_url):
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    'success': False,
                    'error': 'Não foi possível conectar com a planilha. Verifique se está pública.'
                })
            }
        
        # Padroniza dados automaticamente
        analisador_completo._padronizar_todos_dados()
        
        # Aplica filtro por data se especificado
        if data_inicio or data_fim:
            analisador_completo._aplicar_filtro_data(data_inicio, data_fim)
        
        # Converte para formato compatível
        adaptador = AdaptadorDados()
        dados_segmentados = adaptador.converter_para_formato_antigo(analisador_completo.dados_abas, data_inicio, data_fim)
        
        if not dados_segmentados or dados_segmentados.get('todos') is None or len(dados_segmentados.get('todos', [])) == 0:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    'success': False,
                    'error': 'Nenhum dado encontrado. O sistema adaptativo analisou todas as abas mas não encontrou estrutura reconhecível com colunas de avaliação/feedback.'
                })
            }
        
        dados = dados_segmentados['todos']
        
        # 2. ANÁLISE INTELIGENTE COM IA
        analisador_ia = AnalisadorIACustomizado(dados_segmentados, loja_nome)
        relatorio_ia = analisador_ia.gerar_analise_completa()
        
        if not relatorio_ia:
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    'success': False,
                    'error': 'Erro na análise inteligente dos dados.'
                })
            }
        
        # 3. GERAÇÃO DO DOCUMENTO
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo_doc = f"analise_pos_venda_{loja_nome.replace(' ', '_')}_{timestamp}.docx"
        
        try:
            caminho_arquivo = gerar_doc_inteligente(relatorio_ia, loja_nome, nome_arquivo_doc)
            
            if not caminho_arquivo:
                return {
                    'statusCode': 500,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Content-Type': 'application/json',
                    },
                    'body': json.dumps({
                        'success': False,
                        'error': 'Função gerar_doc_inteligente retornou None'
                    })
                }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    'success': False,
                    'error': f'Erro na geração do relatório: {str(e)}'
                })
            }
        
        # Extrair apenas o nome do arquivo
        nome_arquivo = os.path.basename(caminho_arquivo)
        
        # Calcular métricas básicas para o frontend
        nps_score = 0
        avg_rating = 0
        vendedores_count = 0
        
        # Tentar extrair métricas básicas dos dados
        try:
            # Buscar colunas de avaliação
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
            
            # Contar vendedores únicos
            col_vendedor = None
            for col in dados.columns:
                col_lower = str(col).lower()
                if any(palavra in col_lower for palavra in ['vendedor', 'atendente', 'consultor', 'funcionario']):
                    col_vendedor = col
                    break
            
            if col_vendedor:
                vendedores_unicos = dados[col_vendedor].dropna().nunique()
                vendedores_count = int(vendedores_unicos)
                
        except Exception as e:
            # Garantir valores padrão em caso de erro
            nps_score = 0
            avg_rating = 0
            vendedores_count = 0
        
        # Retornar resultado
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
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json',
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json',
            },
            'body': json.dumps({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            })
        }