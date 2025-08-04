import json
import csv
import requests
import re
from datetime import datetime
from io import StringIO
import os

def handler(request):
    """Vercel serverless function simplificada para análise de dados"""
    
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
        
        # Extrai ID da planilha
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheets_url)
        if not sheet_id_match:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    'success': False,
                    'error': 'ID da planilha não encontrado na URL'
                })
            }
        
        sheet_id = sheet_id_match.group(1)
        
        # Baixa dados CSV da primeira aba
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
        response = requests.get(csv_url, timeout=30)
        
        if response.status_code != 200:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    'success': False,
                    'error': 'Planilha não está pública ou não existe'
                })
            }
        
        # Processa CSV
        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)
        dados = list(reader)
        
        if not dados:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    'success': False,
                    'error': 'Nenhum dado encontrado na planilha'
                })
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
        
        # Análise com OpenAI
        relatorio_texto = ""
        try:
            from openai import OpenAI
            api_key = os.environ.get('OPENAI_API_KEY')
            
            if api_key:
                client = OpenAI(api_key=api_key)
                
                # Preparar dados para IA
                resumo_dados = f"""
                Dados da análise NPS:
                - Loja: {loja_nome}
                - Total de registros: {total_registros}
                - NPS Score: {nps_score:.1f}%
                - Avaliação média: {avg_rating:.1f}/10
                - Colunas encontradas: {list(dados[0].keys()) if dados else []}
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # Modelo mais barato
                    messages=[
                        {"role": "system", "content": "Você é um analista de NPS especializado. Gere um relatório profissional em português com insights e recomendações."},
                        {"role": "user", "content": f"Analise estes dados de NPS e gere um relatório: {resumo_dados}"}
                    ],
                    max_tokens=800,
                    temperature=0.7
                )
                
                relatorio_texto = response.choices[0].message.content
            else:
                relatorio_texto = f"""
# Relatório de Análise NPS - {loja_nome}

## Métricas Gerais
- **Total de registros**: {total_registros}
- **NPS Score**: {nps_score:.1f}%
- **Avaliação média**: {avg_rating:.1f}/10

## Resumo
Análise realizada com {total_registros} registros da planilha.
Score NPS de {nps_score:.1f}% indica {"excelente" if nps_score > 70 else "bom" if nps_score > 50 else "regular"} desempenho.

Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}.
                """
        except Exception as e:
            # Fallback se IA falhar
            relatorio_texto = f"""
# Relatório de Análise NPS - {loja_nome}

## Métricas Gerais
- **Total de registros**: {total_registros}
- **NPS Score**: {nps_score:.1f}%
- **Avaliação média**: {avg_rating:.1f}/10

## Resumo
Análise realizada com {total_registros} registros da planilha.
Score NPS de {nps_score:.1f}% indica {"excelente" if nps_score > 70 else "bom" if nps_score > 50 else "regular"} desempenho.

Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}.

*Nota: Análise IA temporariamente indisponível.*
            """
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json',
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
                'relatorio': relatorio_texto,
                'tipo_relatorio': 'Análise NPS - Versão Simplificada'
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
                'error': f'Erro interno: {str(e)}'
            })
        }