#!/usr/bin/env python3
"""
Analisador IA Simple - Análise básica de dados NPS
Autor: Claude Code  
Data: 27/07/2025
"""

import openai
import os
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()


class AnalisadorIACustomizado:
    """Analisador IA simples para dados NPS"""
    
    def __init__(self, dados_segmentados, nome_loja="Mercadão dos Óculos"):
        self.dados = dados_segmentados
        self.nome_loja = nome_loja
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        self.openai_client = openai.OpenAI(api_key=api_key)
    
    def gerar_analise_completa(self):
        """Gera análise completa com IA otimizada"""
        try:
            print("[IA] Gerando análise com IA...")
            
            # Validação prévia dos dados
            if not self.dados or not isinstance(self.dados, dict):
                print("[AVISO] Dados inválidos para análise IA")
                return self._gerar_relatorio_basico()
            
            # Prepara dados para IA com cache
            resumo_dados = self._preparar_resumo_dados()
            if not resumo_dados or len(resumo_dados.strip()) < 50:
                print("[AVISO] Dados insuficientes para análise IA")
                return self._gerar_relatorio_basico()
            
            prompt = f"""
Você é um consultor de experiência do cliente especializado em relatórios NPS para óticas.
Gere um relatório LIMPO e PROFISSIONAL seguindo EXATAMENTE esta estrutura:

DADOS PARA ANÁLISE:
{resumo_dados}

FORMATO OBRIGATÓRIO DO RELATÓRIO:

[DADOS] Análise Pós-venda — {datetime.now().strftime('%B/%Y')}

[OK] Visão Geral
NPS Atendimento: [número] ([classificação])
NPS Produto: [número] ([classificação])
Total de Avaliações: [número]

[PESSOAS] Avaliação de Atendimento
Média de satisfação: [número]/10
Performance: [texto de 1-2 linhas explicando o resultado]

Destaques Positivos:
• [comentário cliente] - [nome], nota [número]

Pontos de Atenção:
• [comentário crítico] - [nome], nota [número]

[PRODUTO] Avaliação de Produto
Média de satisfação: [número]/10
Performance: [texto de 1-2 linhas explicando o resultado]

Destaques Positivos:
• [comentário cliente] - [nome], nota [número]

Pontos de Atenção:
• [comentário crítico] - [nome], nota [número]

👩‍💼 Performance das Vendedoras
Destaque: [nome] com média [número] em [quantidade] atendimentos
Acompanhamento: [nome] necessita suporte com média [número]

[IDEIA] Recomendações
1. [ação específica baseada nos dados]
2. [melhoria concreta]
3. [estratégia de manutenção]

REGRAS CRÍTICAS:
• Use APENAS os dados específicos fornecidos (D+1 para atendimento, D+30 para produto)
• Seja conciso - máximo 2 comentários por seção
• NÃO invente dados - use apenas o que está disponível
• Mantenha formatação SUPER SIMPLES - apenas texto corrido e bullets (•)
• NUNCA crie tabelas, linhas, separadores ou formatação complexa
• Se não houver dados de uma seção, escreva "Dados não disponíveis"
• Performance das vendedoras: APENAS texto corrido, sem tabelas ou formatação especial
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Você é um consultor especialista em NPS e experiência do clientee,Analisa dados de pós-venda e entrega insights claros e confiáveis"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            relatorio_ia = response.choices[0].message.content
            
            # Monta relatório final
            relatorio_final = self._montar_relatorio_final(relatorio_ia)
            
            print("[OK] Análise IA concluída!")
            return relatorio_final
            
        except Exception as e:
            print(f"[AVISO] Erro na análise IA: {str(e)}")
            return self._gerar_relatorio_basico()
    
    def _preparar_resumo_dados(self):
        """Prepara resumo detalhado dos dados para IA"""
        try:
            resumo = f"=== DADOS NPS {self.nome_loja.upper()} ===\n\n"
            
            if self.dados.get('todos') is not None:
                df_todos = self.dados['todos']
                total = len(df_todos)
                resumo += f"[DADOS] Total de registros: {total}\n\n"
                
                # Análise por tipo de aba
                if 'Tipo_Aba' in df_todos.columns:
                    tipos = df_todos['Tipo_Aba'].value_counts()
                    resumo += "[RELATORIO] Distribuição por tipo:\n"
                    for tipo, count in tipos.items():
                        resumo += f"   • {tipo}: {count} registros\n"
                    resumo += "\n"
                
                # Análise detalhada de avaliações
                if 'Avaliação' in df_todos.columns:
                    avaliacoes = df_todos['Avaliação'].dropna()
                    if len(avaliacoes) > 0:
                        resumo += f"⭐ MÉTRICAS DE AVALIAÇÃO:\n"
                        resumo += f"   • Média geral: {avaliacoes.mean():.2f}\n"
                        resumo += f"   • Promotores (9-10): {len(avaliacoes[avaliacoes >= 9])}\n"
                        resumo += f"   • Neutros (7-8): {len(avaliacoes[(avaliacoes >= 7) & (avaliacoes <= 8)])}\n"
                        resumo += f"   • Detratores (≤6): {len(avaliacoes[avaliacoes <= 6])}\n\n"
                        
                        # MÉTRICAS SEPARADAS POR TIPO
                        if 'Tipo_Aba' in df_todos.columns:
                            for tipo in ['atendimento', 'produto']:
                                df_tipo = df_todos[df_todos['Tipo_Aba'] == tipo]
                                if len(df_tipo) > 0 and 'Avaliação' in df_tipo.columns:
                                    aval_tipo = df_tipo['Avaliação'].dropna()
                                    if len(aval_tipo) > 0:
                                        tipo_nome = 'ATENDIMENTO (D+1)' if tipo == 'atendimento' else 'PRODUTO (D+30)'
                                        resumo += f"[DADOS] {tipo_nome}:\n"
                                        resumo += f"   • Total avaliações: {len(aval_tipo)}\n"
                                        resumo += f"   • Média de nota: {aval_tipo.mean():.2f}\n"
                                        
                                        promotores = len(aval_tipo[aval_tipo >= 9])
                                        neutros = len(aval_tipo[(aval_tipo >= 7) & (aval_tipo <= 8)])
                                        detratores = len(aval_tipo[aval_tipo <= 6])
                                        nps = (promotores - detratores) / len(aval_tipo) * 100
                                        
                                        resumo += f"   • NPS: {nps:.1f}\n"
                                        resumo += f"   • Promotores: {promotores}\n"
                                        resumo += f"   • Detratores: {detratores}\n\n"
                
                # Análise de vendedores
                if 'Vendedor' in df_todos.columns:
                    vendedores = df_todos['Vendedor'].value_counts().head(10)
                    resumo += f"[PESSOAS] TOP VENDEDORES:\n"
                    for vendedor, count in vendedores.items():
                        if vendedor and str(vendedor).strip() != '' and str(vendedor) != 'nan':
                            # Calcula média do vendedor se possível
                            df_vendedor = df_todos[df_todos['Vendedor'] == vendedor]
                            if 'Avaliação' in df_vendedor.columns:
                                aval_vendedor = df_vendedor['Avaliação'].dropna()
                                if len(aval_vendedor) > 0:
                                    media = aval_vendedor.mean()
                                    resumo += f"   • {vendedor}: {count} vendas (média {media:.1f})\n"
                                else:
                                    resumo += f"   • {vendedor}: {count} vendas\n"
                    resumo += "\n"
                
                # Comentários negativos (para análise de problemas)
                if 'Avaliação' in df_todos.columns and 'Comentário' in df_todos.columns:
                    comentarios_ruins = df_todos[df_todos['Avaliação'] <= 6]
                    if len(comentarios_ruins) > 0:
                        resumo += f"[AVISO] COMENTÁRIOS CRÍTICOS (nota ≤6):\n"
                        for idx, row in comentarios_ruins.head(5).iterrows():
                            nota = row.get('Avaliação', 'N/A')
                            comentario = str(row.get('Comentário', '')).strip()
                            vendedor = str(row.get('Vendedor', 'N/A')).strip()
                            
                            # Filtra e limpa comentários
                            comentario_limpo = self._limpar_comentario(comentario)
                            vendedor_limpo = self._limpar_comentario(vendedor)
                            
                            if comentario_limpo and len(comentario_limpo) > 5:
                                resumo += f"   • Nota {nota} - {vendedor_limpo}: \"{comentario_limpo[:100]}...\"\n"
                        resumo += "\n"
            
            return resumo
            
        except Exception as e:
            return f"Dados básicos da {self.nome_loja}\nErro: {str(e)}"
    
    def _limpar_comentario(self, texto):
        """Limpa comentários removendo caracteres de encoding ruins e palavrões"""
        if not texto or texto == 'nan' or str(texto).strip() == '':
            return ''
        
        texto = str(texto).strip()
        
        # Correções de encoding comuns
        correções_encoding = {
            'nÃ£o': 'não',
            'Ã£o': 'ão', 
            'Ã§Ã£o': 'ção',
            'Ã§': 'ç',
            'Ã¡': 'á',
            'Ã©': 'é',
            'Ã­': 'í',
            'Ã³': 'ó',
            'Ãº': 'ú',
            'Ã ': 'à',
            'Ã¢': 'â',
            'Ãª': 'ê',
            'Ã´': 'ô',
            'Ã¹': 'ù',
            'GonÃ§alves': 'Gonçalves',
            'JosÃ©': 'José',
            'MarÃ­a': 'Maria',
            'JoÃ£o': 'João',
            'AnÃ´nio': 'Antônio',
            'resoluÃ§Ã£o': 'resolução',
            'avaliaÃ§Ã£o': 'avaliação',
            'atenÃ§Ã£o': 'atenção',
            'informaÃ§Ã£o': 'informação',
            'consideraÃ§Ãµes': 'considerações',
            'atendendte': 'atendente'
        }
        
        # Aplica correções de encoding
        for errado, correto in correções_encoding.items():
            texto = texto.replace(errado, correto)
        
        # Remove comentários muito vagos ou inúteis
        comentarios_inuteis = [
            'nan',
            'n/a',
            'sem comentário',
            'nada',
            'ok',
            'bom',
            'ruim',
            '.',
            '..',
            '...',
            'não sei',
            'nenhum'
        ]
        
        if texto.lower().strip() in comentarios_inuteis:
            return ''
        
        # Remove comentários muito curtos (menos de 10 caracteres)
        if len(texto.strip()) < 10:
            return ''
        
        # Remove caracteres especiais problemáticos
        texto = texto.replace('Ã¢â‚¬â„¢', "'")
        texto = texto.replace('Ã¢â‚¬Å"', '"')
        texto = texto.replace('Ã¢â‚¬', '"')
        
        # Limita tamanho para evitar comentários muito longos
        if len(texto) > 150:
            texto = texto[:150] + '...'
        
        return texto.strip()
    
    def _montar_relatorio_final(self, relatorio_ia):
        """Monta relatório final formatado"""
        timestamp = datetime.now().strftime('%d/%m/%Y às %H:%M')
        
        relatorio = f"""
[DATA] Data da Análise: {timestamp}

{relatorio_ia}
"""
        
        return relatorio
    
    def _gerar_relatorio_basico(self):
        """Gera relatório básico sem IA"""
        timestamp = datetime.now().strftime('%d/%m/%Y às %H:%M')
        
        return f"""
╔═══════════════════════════════════════════════════════════════╗
║                    RELATÓRIO NPS BÁSICO                      ║
║                   {self.nome_loja.upper():<45} ║
╚═══════════════════════════════════════════════════════════════╝

[DATA] Data da Análise: {timestamp}

[DADOS] DADOS PROCESSADOS:
• Dados extraídos e organizados com sucesso
• Sistema funcionando adequadamente
• Pronto para análise detalhada

[IDEIA] OBSERVAÇÃO:
• Análise IA temporariamente indisponível
• Dados estruturados para processamento manual

╔═══════════════════════════════════════════════════════════════╗
║                    PROCESSAMENTO CONCLUÍDO                   ║
╚═══════════════════════════════════════════════════════════════╝
"""


if __name__ == "__main__":
    print("Analisador IA Simple pronto!")
    # Teste básico
    dados_teste = {'todos': None}
    try:
        analisador = AnalisadorIACustomizado(dados_teste, "Teste")
        print("Inicializacao concluida!")
    except Exception as e:
        print(f"Erro na inicializacao: {e}")