import json
import re
import csv
from io import StringIO

def handler(request):
    """Analyze endpoint - análise básica de planilhas"""
    
    # Handle CORS preflight
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
            data = request.get_json() or {}
        elif hasattr(request, 'body'):
            data = json.loads(request.body) if request.body else {}
        else:
            data = {}
        
        sheets_url = data.get('sheets_url', '')
        loja_nome = data.get('loja_nome', 'Análise NPS')
        
        if not sheets_url:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({'success': False, 'error': 'URL da planilha é obrigatória'})
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
        
        # Baixa dados da planilha
        try:
            import urllib.request
            
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
            
            with urllib.request.urlopen(csv_url, timeout=15) as response:
                csv_content = response.read().decode('utf-8')
                
                if response.status != 200 or len(csv_content) < 50:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*',
                        },
                        'body': json.dumps({'success': False, 'error': 'Planilha não está pública ou vazia'})
                    }
                
                # Processa CSV
                csv_data = StringIO(csv_content)
                reader = csv.DictReader(csv_data)
                dados = list(reader)
                
                if not dados:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*',
                        },
                        'body': json.dumps({'success': False, 'error': 'Nenhum dado encontrado na planilha'})
                    }
                
                # Análise básica
                total_registros = len(dados)
                
                # Procura coluna de avaliação
                col_avaliacao = None
                for col in dados[0].keys():
                    if any(palavra in col.lower() for palavra in ['avaliacao', 'avaliação', 'nota', 'score', 'rating']):
                        col_avaliacao = col
                        break
                
                nps_score = 0
                avg_rating = 0
                
                if col_avaliacao:
                    avaliacoes = []
                    for row in dados:
                        try:
                            val = float(row[col_avaliacao])
                            if 0 <= val <= 10:
                                avaliacoes.append(val)
                        except (ValueError, TypeError):
                            continue
                    
                    if avaliacoes:
                        avg_rating = sum(avaliacoes) / len(avaliacoes)
                        promotores = sum(1 for x in avaliacoes if x >= 9)
                        detratores = sum(1 for x in avaliacoes if x <= 6)
                        nps_score = ((promotores - detratores) / len(avaliacoes)) * 100
                
                # Gera relatório básico
                relatorio = f"""# Relatório NPS - {loja_nome}

## Métricas Principais
- **Total de registros**: {total_registros}
- **NPS Score**: {nps_score:.1f}%
- **Avaliação média**: {avg_rating:.1f}/10

## Análise Resumida
{"Excelente desempenho!" if nps_score > 70 else "Bom desempenho!" if nps_score > 50 else "Desempenho regular - há espaço para melhorias"}

Análise realizada com {total_registros} registros da planilha.
Data: 2025-01-04
"""
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    'body': json.dumps({
                        'success': True,
                        'message': 'Análise concluída com sucesso!',
                        'dados': {
                            'total_registros': total_registros,
                            'nps_score': round(nps_score, 1),
                            'avg_rating': round(avg_rating, 1),
                            'loja_nome': loja_nome
                        },
                        'relatorio': relatorio,
                        'tipo_relatorio': 'Análise NPS Básica'
                    })
                }
                
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({'success': False, 'error': f'Erro ao processar planilha: {str(e)}'})
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