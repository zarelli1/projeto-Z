#!/usr/bin/env python3
"""
Gerador de PDF Customizado - Estilo Mercadão dos Óculos com WeasyPrint
Autor: Claude Code
Data: 27/07/2025
"""

from weasyprint import HTML, CSS
from datetime import datetime
import textwrap
import re
import os


class PDFGeneratorAdaptativo:
    """Gerador de PDF adaptativo que se ajusta automaticamente ao tipo de dados"""
    
    def __init__(self):
        self.css = self._estilos_css()
        self.templates = self._criar_templates()
    
    def _criar_templates(self):
        """Define templates para diferentes tipos de dados"""
        return {
            'nps_completo': {
                'titulo': '📊 Relatório Completo de NPS',
                'secoes': ['metricas', 'analise', 'comentarios', 'recomendacoes']
            },
            'metricas_simples': {
                'titulo': '📈 Relatório de Métricas',
                'secoes': ['metricas', 'insights']
            },
            'analise_ia': {
                'titulo': '🤖 Análise Inteligente',
                'secoes': ['resumo', 'insights', 'acoes']
            },
            'relatorio_vendedores': {
                'titulo': '👥 Performance de Vendedores',
                'secoes': ['ranking', 'detalhes', 'melhorias']
            }
        }
    
    def _estilos_css(self):
        """Estilos CSS para o gerador adaptativo"""
        return """
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'DejaVu Sans', sans-serif;
            font-size: 11pt;
            color: #2C3E50;
            line-height: 1.6;
        }
        .titulo {
            font-size: 24pt;
            font-weight: 700;
            color: #154360;
            text-align: center;
            margin-bottom: 5px;
        }
        .subtitulo {
            font-size: 14pt;
            color: #1F618D;
            text-align: center;
            margin-bottom: 30px;
        }
        .secao {
            font-size: 16pt;
            font-weight: bold;
            color: #2E4053;
            margin-top: 40px;
            border-left: 6px solid #2980B9;
            padding-left: 12px;
        }
        .metrica {
            background: #F8F9F9;
            padding: 12px 16px;
            margin: 10px 0;
            border-left: 5px solid #7D3C98;
            font-weight: 600;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .comentario {
            font-style: italic;
            color: #566573;
            background: #FBFCFC;
            padding: 10px 14px;
            margin: 6px 0;
            border-left: 4px solid #5DADE2;
            border-radius: 3px;
        }
        .alerta {
            background: #FDEDEC;
            color: #922B21;
            border-left: 5px solid #C0392B;
            padding: 12px 16px;
            font-weight: bold;
            margin: 12px 0;
            border-radius: 4px;
        }
        .lista {
            padding-left: 25px;
            margin: 12px 0;
        }
        .lista li {
            margin-bottom: 6px;
        }
        .tabela {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 10.5pt;
        }
        .tabela th, .tabela td {
            border: 1px solid #D5D8DC;
            padding: 10px;
        }
        .tabela th {
            background-color: #2E86C1;
            color: white;
            text-align: left;
        }
        .tabela tr:nth-child(even) {
            background-color: #F4F6F7;
        }
        """
    
    def gerar_pdf_adaptativo(self, dados, nome_loja="Unidade", nome_arquivo=None):
        """
        Gera PDF adaptativo baseado no tipo de dados fornecido
        
        Args:
            dados: Pode ser dict, list, string ou dados estruturados
            nome_loja: Nome da loja/unidade
            nome_arquivo: Nome personalizado do arquivo
        """
        try:
            # Detecta tipo de dados automaticamente
            tipo_dados = self._detectar_tipo_dados(dados)
            print(f"🔍 Tipo de dados detectado: {tipo_dados}")
            
            # Converte dados para formato estruturado
            dados_estruturados = self._estruturar_dados(dados, tipo_dados)
            
            # Seleciona template apropriado
            template = self._selecionar_template(tipo_dados, dados_estruturados)
            
            # Gera HTML com template selecionado
            html = self._gerar_html_adaptativo(dados_estruturados, template, nome_loja)
            
            if not nome_arquivo:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nome_arquivo = f"relatorio_{tipo_dados}_{nome_loja.replace(' ', '_').lower()}_{timestamp}.pdf"
            
            # Criar diretório se não existir
            if not os.path.exists('relatorios'):
                os.makedirs('relatorios')
            
            caminho_completo = os.path.join('relatorios', nome_arquivo)
            HTML(string=html).write_pdf(caminho_completo, stylesheets=[CSS(string=self.css)])
            
            print(f"✅ PDF adaptativo gerado: {caminho_completo}")
            return caminho_completo
            
        except Exception as e:
            print(f"❌ Erro ao gerar PDF adaptativo: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _detectar_tipo_dados(self, dados):
        """Detecta automaticamente o tipo de dados"""
        if isinstance(dados, str):
            # Análise de texto/IA
            if any(palavra in dados.lower() for palavra in ['nps', 'net promoter', 'satisfação']):
                return 'analise_nps'
            elif any(palavra in dados.lower() for palavra in ['vendedor', 'performance', 'ranking']):
                return 'relatorio_vendedores'
            else:
                return 'analise_ia'
        
        elif isinstance(dados, dict):
            # Dados estruturados em dicionário
            if 'nps' in str(dados).lower() and 'metricas' in str(dados).lower():
                return 'nps_completo'
            elif 'vendedores' in str(dados).lower():
                return 'relatorio_vendedores'
            else:
                return 'metricas_simples'
        
        elif isinstance(dados, list):
            # Lista de dados estruturados
            if len(dados) > 0 and isinstance(dados[0], dict):
                if 'tipo' in dados[0]:
                    return 'dados_estruturados'
                else:
                    return 'tabela_dados'
            else:
                return 'lista_simples'
        
        else:
            return 'generico'
    
    def _estruturar_dados(self, dados, tipo_dados):
        """Converte dados para formato estruturado padronizado"""
        if tipo_dados == 'dados_estruturados':
            return dados  # Já estruturado
        
        elif isinstance(dados, str):
            # Converte texto em seções estruturadas
            return self._processar_texto_para_estrutura(dados)
        
        elif isinstance(dados, dict):
            # Converte dict para formato de blocos
            return self._processar_dict_para_estrutura(dados)
        
        elif isinstance(dados, list):
            # Converte lista para tabela ou blocos
            return self._processar_lista_para_estrutura(dados)
        
        else:
            # Fallback para dados não reconhecidos
            return [{"tipo": "comentario", "conteudo": str(dados)}]
    
    def _processar_texto_para_estrutura(self, texto):
        """Converte texto livre em estrutura de blocos"""
        blocos = []
        linhas = texto.split('\n')
        
        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue
            
            # Remove formatação Markdown (asteriscos)
            linha_limpa = self._limpar_formatacao_markdown(linha)
            
            # Detecta títulos (começam com emoji ou têm formatação especial)
            if self._eh_titulo(linha_limpa):
                blocos.append({"tipo": "titulo", "conteudo": linha_limpa})
            
            # Detecta métricas (contêm números e %)
            elif self._eh_metrica(linha_limpa):
                blocos.append({"tipo": "metrica", "conteudo": linha_limpa})
            
            # Detecta alertas (palavras de alerta)
            elif self._eh_alerta(linha_limpa):
                blocos.append({"tipo": "alerta", "conteudo": linha_limpa})
            
            # Texto normal
            else:
                blocos.append({"tipo": "comentario", "conteudo": linha_limpa})
        
        return blocos
    
    def _processar_dict_para_estrutura(self, dados_dict):
        """Converte dicionário em blocos estruturados"""
        blocos = []
        
        for chave, valor in dados_dict.items():
            # Título da seção
            blocos.append({"tipo": "titulo", "conteudo": f"📋 {chave.replace('_', ' ').title()}"})
            
            if isinstance(valor, dict):
                # Sub-dicionário como métricas
                for sub_chave, sub_valor in valor.items():
                    blocos.append({"tipo": "metrica", "conteudo": f"{sub_chave}: {sub_valor}"})
            
            elif isinstance(valor, list):
                # Lista como bullets
                if valor:
                    blocos.append({"tipo": "lista", "itens": [str(item) for item in valor]})
            
            else:
                # Valor simples
                blocos.append({"tipo": "metrica", "conteudo": f"{chave}: {valor}"})
        
        return blocos
    
    def _processar_lista_para_estrutura(self, dados_lista):
        """Converte lista em tabela ou blocos"""
        if not dados_lista:
            return [{"tipo": "comentario", "conteudo": "Nenhum dado disponível"}]
        
        # Se são dicts, cria tabela
        if isinstance(dados_lista[0], dict):
            colunas = list(dados_lista[0].keys())
            linhas = [[str(item.get(col, '')) for col in colunas] for item in dados_lista]
            
            return [{
                "tipo": "tabela",
                "colunas": colunas,
                "linhas": linhas
            }]
        
        # Se são strings/números, cria lista
        else:
            return [{"tipo": "lista", "itens": [str(item) for item in dados_lista]}]
    
    def _eh_titulo(self, linha):
        """Verifica se linha é um título"""
        emojis = ['📊', '✅', '⚠️', '📈', '👥', '💡', '🎯', '🏪', '📋', '🔍']
        return any(emoji in linha for emoji in emojis) or linha.isupper()
    
    def _eh_metrica(self, linha):
        """Verifica se linha é uma métrica"""
        return '%' in linha or 'NPS' in linha or re.search(r'\d+[.,]\d+', linha)
    
    def _eh_alerta(self, linha):
        """Verifica se linha é um alerta"""
        palavras_alerta = ['atenção', 'cuidado', 'problema', 'crítico', 'alerta', 'ruim']
        return any(palavra in linha.lower() for palavra in palavras_alerta)
    
    def _limpar_formatacao_markdown(self, texto):
        """Remove formatação Markdown como asteriscos"""
        import re
        # Remove asteriscos de formatação bold (**texto**)
        texto_limpo = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)
        # Remove asteriscos simples (*texto*)
        texto_limpo = re.sub(r'\*(.*?)\*', r'\1', texto_limpo)
        return texto_limpo
    
    def _selecionar_template(self, tipo_dados, dados_estruturados):
        """Seleciona template mais apropriado"""
        # Analisa conteúdo para refinar seleção
        conteudo_str = str(dados_estruturados).lower()
        
        if 'nps' in conteudo_str and 'metrica' in conteudo_str:
            return self.templates['nps_completo']
        elif 'vendedor' in conteudo_str or 'ranking' in conteudo_str:
            return self.templates['relatorio_vendedores']
        elif len([b for b in dados_estruturados if b.get('tipo') == 'metrica']) > 3:
            return self.templates['metricas_simples']
        else:
            return self.templates['analise_ia']
    
    def _gerar_html_adaptativo(self, dados_estruturados, template, nome_loja):
        """Gera HTML usando template selecionado"""
        html = f"""
        <html lang='pt-BR'>
        <head><meta charset='utf-8'></head>
        <body>
            <div class='titulo'>{template['titulo']}</div>
            <div class='subtitulo'>Mercadão dos Óculos — {nome_loja}</div>
        """
        
        # Adiciona conteúdo baseado no template
        for bloco in dados_estruturados:
            tipo = bloco.get("tipo")
            if tipo == "titulo":
                html += f"<div class='secao'>{bloco['conteudo']}</div>"
            elif tipo == "metrica":
                html += f"<div class='metrica'>{bloco['conteudo']}</div>"
            elif tipo == "comentario":
                html += f"<div class='comentario'>{bloco['conteudo']}</div>"
            elif tipo == "alerta":
                html += f"<div class='alerta'>{bloco['conteudo']}</div>"
            elif tipo == "lista":
                html += "<ul class='lista'>" + ''.join([f"<li>{item}</li>" for item in bloco['itens']]) + "</ul>"
            elif tipo == "tabela":
                html += "<table class='tabela'>"
                html += "<tr>" + ''.join([f"<th>{col}</th>" for col in bloco['colunas']]) + "</tr>"
                for linha in bloco['linhas']:
                    html += "<tr>" + ''.join([f"<td>{celula}</td>" for celula in linha]) + "</tr>"
                html += "</table>"
        
        html += "</body></html>"
        return html

class PDFGeneratorV2:
    def __init__(self):
        self.css = self._estilos_css()

    def _estilos_css(self):
        return """
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'DejaVu Sans', sans-serif;
            font-size: 11pt;
            color: #2C3E50;
            line-height: 1.6;
        }
        .titulo {
            font-size: 24pt;
            font-weight: 700;
            color: #154360;
            text-align: center;
            margin-bottom: 5px;
        }
        .subtitulo {
            font-size: 14pt;
            color: #1F618D;
            text-align: center;
            margin-bottom: 30px;
        }
        .secao {
            font-size: 16pt;
            font-weight: bold;
            color: #2E4053;
            margin-top: 40px;
            border-left: 6px solid #2980B9;
            padding-left: 12px;
        }
        .metrica {
            background: #F8F9F9;
            padding: 12px 16px;
            margin: 10px 0;
            border-left: 5px solid #7D3C98;
            font-weight: 600;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .comentario {
            font-style: italic;
            color: #566573;
            background: #FBFCFC;
            padding: 10px 14px;
            margin: 6px 0;
            border-left: 4px solid #5DADE2;
            border-radius: 3px;
        }
        .alerta {
            background: #FDEDEC;
            color: #922B21;
            border-left: 5px solid #C0392B;
            padding: 12px 16px;
            font-weight: bold;
            margin: 12px 0;
            border-radius: 4px;
        }
        .lista {
            padding-left: 25px;
            margin: 12px 0;
        }
        .lista li {
            margin-bottom: 6px;
        }
        .tabela {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 10.5pt;
        }
        .tabela th, .tabela td {
            border: 1px solid #D5D8DC;
            padding: 10px;
        }
        .tabela th {
            background-color: #2E86C1;
            color: white;
            text-align: left;
        }
        .tabela tr:nth-child(even) {
            background-color: #F4F6F7;
        }
        """

    def gerar_pdf(self, dados, nome_loja="Unidade", nome_arquivo=None):
        if not nome_arquivo:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"relatorio_mdo_{nome_loja.replace(' ', '_').lower()}_{timestamp}.pdf"

        html = self._gerar_html(dados, nome_loja)
        HTML(string=html).write_pdf(nome_arquivo, stylesheets=[CSS(string=self.css)])
        print(f"✅ PDF v2 gerado com sucesso: {nome_arquivo}")
        return nome_arquivo

    def _gerar_html(self, dados, nome_loja):
        html = f"""
        <html lang='pt-BR'>
        <head><meta charset='utf-8'></head>
        <body>
            <div class='titulo'>📊 Relatório de Pós-venda</div>
            <div class='subtitulo'>Mercadão dos Óculos — {nome_loja}</div>
        """

        for bloco in dados:
            tipo = bloco.get("tipo")
            if tipo == "titulo":
                html += f"<div class='secao'>{bloco['conteudo']}</div>"
            elif tipo == "metrica":
                html += f"<div class='metrica'>{bloco['conteudo']}</div>"
            elif tipo == "comentario":
                html += f"<div class='comentario'>{bloco['conteudo']}</div>"
            elif tipo == "alerta":
                html += f"<div class='alerta'>{bloco['conteudo']}</div>"
            elif tipo == "lista":
                html += "<ul class='lista'>" + ''.join([f"<li>{item}</li>" for item in bloco['itens']]) + "</ul>"
            elif tipo == "tabela":
                html += "<table class='tabela'>"
                html += "<tr>" + ''.join([f"<th>{col}</th>" for col in bloco['colunas']]) + "</tr>"
                for linha in bloco['linhas']:
                    html += "<tr>" + ''.join([f"<td>{celula}</td>" for celula in linha]) + "</tr>"
                html += "</table>"

        html += "</body></html>"
        return html


class GeradorPDFCustomizado:
    """Gerador de PDF customizado para compatibilidade com sistema existente"""
    
    def __init__(self):
        """Inicializa gerador com estilo customizado"""
        self.css_styles = self._criar_estilos_css()
    
    def _limpar_formatacao_markdown(self, texto):
        """Remove formatação Markdown como asteriscos"""
        import re
        # Remove asteriscos de formatação bold (**texto**)
        texto_limpo = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)
        # Remove asteriscos simples (*texto*)
        texto_limpo = re.sub(r'\*(.*?)\*', r'\1', texto_limpo)
        return texto_limpo
    
    def _criar_estilos_css(self):
        """Cria estilos CSS customizados para Mercadão dos Óculos"""
        return """
        @page {
            size: A4;
            margin: 2cm 1.5cm 3cm 1.5cm;
        }
        
        body {
            font-family: Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #2C3E50;
            margin: 0;
            padding: 0;
        }
        
        /* Título principal */
        .titulo-relatorio {
            font-size: 22pt;
            font-weight: bold;
            color: #1B4F72;
            text-align: center;
            margin-bottom: 8px;
            margin-top: 0;
        }
        
        /* Subtítulo empresa */
        .subtitulo-empresa {
            font-size: 16pt;
            font-weight: bold;
            color: #2E86AB;
            text-align: center;
            margin-bottom: 6px;
            margin-top: 4px;
        }
        
        /* Data e período */
        .data-periodo {
            font-size: 12pt;
            color: #2C3E50;
            text-align: center;
            margin-bottom: 20px;
            margin-top: 4px;
        }
        
        /* Seções principais */
        .secao-principal {
            font-size: 15pt;
            font-weight: bold;
            color: #1B4F72;
            margin-top: 18px;
            margin-bottom: 10px;
            border-left: 4px solid #2E86AB;
            padding-left: 10px;
        }
        
        /* Métricas em destaque */
        .metrica-destaque {
            font-size: 12pt;
            font-weight: bold;
            color: #A23B72;
            margin: 6px 0 8px 10px;
            padding: 5px 10px;
            background-color: #F8F9FA;
            border-left: 3px solid #A23B72;
        }
        
        /* Texto normal do relatório */
        .texto-relatorio {
            font-size: 11pt;
            color: #2C3E50;
            margin: 6px 0;
            text-align: justify;
            padding-left: 5px;
        }
        
        /* Listas com bullets */
        .lista-insights {
            font-size: 11pt;
            color: #2C3E50;
            margin: 3px 0 5px 20px;
            list-style-type: disc;
        }
        
        ul.lista-insights {
            padding-left: 20px;
        }
        
        li.lista-insights {
            margin: 3px 0;
        }
        """
    
    def gerar_pdf_customizado(self, conteudo_ia, nome_loja, nome_arquivo=None):
        """
        Gera PDF customizado a partir do conteúdo da IA usando WeasyPrint
        
        Args:
            conteudo_ia: String com análise da IA
            nome_loja: Nome da loja/empresa
            nome_arquivo: Nome do arquivo (opcional)
        """
        try:
            print("📄 Gerando PDF customizado Mercadão dos Óculos com WeasyPrint...")
            
            if not nome_arquivo:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nome_arquivo = f"analise_pos_venda_{nome_loja.replace(' ', '_')}_{timestamp}.pdf"
            
            # Gera HTML completo
            html_content = self._gerar_html_completo(conteudo_ia, nome_loja)
            
            # Converte para PDF com WeasyPrint
            html_doc = HTML(string=html_content)
            css_doc = CSS(string=self.css_styles)
            
            # Verifica se pasta relatorios existe
            if not os.path.exists('relatorios'):
                os.makedirs('relatorios')
            
            caminho_completo = os.path.join('relatorios', nome_arquivo)
            html_doc.write_pdf(caminho_completo, stylesheets=[css_doc])
            
            print(f"✅ PDF customizado gerado: {caminho_completo}")
            return caminho_completo
            
        except Exception as e:
            print(f"❌ Erro ao gerar PDF customizado: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _gerar_html_completo(self, conteudo_ia, nome_loja):
        """Gera HTML completo do relatório"""
        
        # Header do relatório
        data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M')
        
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Relatório Pós-venda - {nome_loja}</title>
        </head>
        <body>
            <div class="titulo-relatorio">
                📊 Relatório Completo de NPS
            </div>
            
            <div class="subtitulo-empresa">
                Mercadão dos Óculos
            </div>
            
            {f'<div class="data-periodo">Unidade {nome_loja}</div>' if nome_loja and nome_loja != "Sistema" else ''}
            
            <div class="data-periodo">
                Relatório gerado em {data_geracao}
            </div>
            
            <div class="espacador-medio"></div>
            
            {self._processar_conteudo_html(conteudo_ia)}
        </body>
        </html>
        """
        
        return html
    
    def _processar_conteudo_html(self, conteudo):
        """Processa o conteúdo da IA para HTML estilizado"""
        html_elements = []
        
        # Remove formatação Markdown do conteúdo completo
        conteudo_limpo = self._limpar_formatacao_markdown(conteudo)
        
        # Divide o conteúdo em seções
        secoes = self._dividir_em_secoes(conteudo_limpo)
        
        for i, secao in enumerate(secoes):
            if secao['titulo']:
                # Adiciona título da seção
                html_elements.append(f'<div class="secao-principal">{secao["titulo"]}</div>')
            
            # Processa o texto da seção
            html_elements.extend(self._processar_texto_html(secao['texto']))
            
            # Adiciona espaçamento entre seções
            if i < len(secoes) - 1:
                html_elements.append('<div class="espacador-pequeno"></div>')
        
        return '\n'.join(html_elements)
    
    def _dividir_em_secoes(self, conteudo):
        """Divide conteúdo em seções baseado em padrões"""
        secoes = []
        
        linhas = conteudo.split('\n')
        secao_atual = {'titulo': '', 'texto': ''}
        
        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue
            
            # Verifica se é um título de seção (começa com emoji)
            if self._eh_titulo_secao(linha):
                # Salva seção anterior se existir
                if secao_atual['texto']:
                    secoes.append(secao_atual)
                
                # Inicia nova seção
                secao_atual = {'titulo': linha, 'texto': ''}
            else:
                # Adiciona texto à seção atual
                if secao_atual['texto']:
                    secao_atual['texto'] += '\n'
                secao_atual['texto'] += linha
        
        # Adiciona última seção
        if secao_atual['texto']:
            secoes.append(secao_atual)
        
        return secoes
    
    def _eh_titulo_secao(self, linha):
        """Verifica se a linha é um título de seção"""
        # Padrões de títulos (emojis comuns)
        emojis_titulo = ['✅', '📊', '🎯', '🛍️', '⚠️', '👩‍💼', '🏪', '📈', '💡', '📋', '🔍', '📞', '🎉', '👥']
        
        for emoji in emojis_titulo:
            if linha.startswith(emoji):
                return True
        
        return False
    
    def _processar_texto_html(self, texto):
        """Processa texto de uma seção para HTML estilizado"""
        elementos = []
        
        paragrafos = texto.split('\n')
        lista_atual = []
        
        for paragrafo in paragrafos:
            paragrafo = paragrafo.strip()
            if not paragrafo:
                continue
            
            # Fecha lista se necessário
            if lista_atual and not (paragrafo.startswith('•') or paragrafo.startswith('1.') or paragrafo.startswith('2.') or paragrafo.startswith('3.')):
                elementos.append('<ul class="lista-insights">')
                for item in lista_atual:
                    elementos.append(f'<li class="lista-insights">{item}</li>')
                elementos.append('</ul>')
                lista_atual = []
            
            # Listas com bullet points ou numeradas
            if paragrafo.startswith('•') or re.match(r'^\d+\.', paragrafo):
                texto_bullet = paragrafo[1:].strip() if paragrafo.startswith('•') else paragrafo
                lista_atual.append(texto_bullet)
            
            # Texto normal
            else:
                elementos.append(f'<div class="texto-relatorio">{paragrafo}</div>')
        
        # Fecha lista final se necessário
        if lista_atual:
            elementos.append('<ul class="lista-insights">')
            for item in lista_atual:
                elementos.append(f'<li class="lista-insights">{item}</li>')
            elementos.append('</ul>')
        
        return elementos


# Função de conveniência para integração com sistema existente
def gerar_pdf_inteligente(dados, nome_loja="Unidade", nome_arquivo=None):
    """
    Função de conveniência que usa o gerador adaptativo
    Compatível com todos os tipos de dados do sistema
    """
    gerador = PDFGeneratorAdaptativo()
    return gerador.gerar_pdf_adaptativo(dados, nome_loja, nome_arquivo)


# Exemplo de uso e testes
if __name__ == "__main__":
    print("🧪 Testando Gerador PDF Adaptativo")
    
    # Teste 1: Dados estruturados (formato atual)
    exemplo_estruturado = [
        {"tipo": "titulo", "conteudo": "✅ Visão Geral"},
        {"tipo": "metrica", "conteudo": "NPS Atendimento: 92.5"},
        {"tipo": "metrica", "conteudo": "NPS Produto: 88.1"},
        {"tipo": "lista", "itens": ["Total Atendimento: 2672", "Total Produto: 1453"]},
        {"tipo": "titulo", "conteudo": "👥 Comentários de Clientes"},
        {"tipo": "comentario", "conteudo": "\"Excelente atendimento!\" — Maria Silva"},
        {"tipo": "alerta", "conteudo": "⚠️ 23 clientes marcaram nota 6 ou menor no NPS de produto."}
    ]
    
    # Teste 2: Texto de análise IA
    exemplo_texto = """
    📊 Análise de Satisfação NPS - Mercadão dos Óculos
    
    ✅ Métricas Principais
    NPS Atendimento: 85.4%
    NPS Produto: 78.2%
    Total de respostas: 4.125
    
    💡 Insights Principais
    • Clientes elogiam qualidade do atendimento
    • Tempo de entrega é o principal ponto de melhoria
    • Vendedoras Maria e Ana têm melhor performance
    
    ⚠️ Pontos de Atenção
    Crítico: 15% dos clientes relataram problemas com prazo de entrega
    """
    
    # Teste 3: Dicionário de métricas
    exemplo_dict = {
        "nps_metricas": {
            "atendimento": 85.4,
            "produto": 78.2,
            "geral": 81.8
        },
        "vendedores_top": ["Maria Silva", "Ana Santos", "João Pedro"],
        "problemas_criticos": ["Prazo de entrega", "Comunicação pós-venda"]
    }
    
    # Teste 4: Lista de dados tabulares
    exemplo_tabela = [
        {"Vendedor": "Maria", "NPS": 92.1, "Vendas": 45},
        {"Vendedor": "Ana", "NPS": 88.5, "Vendas": 38},
        {"Vendedor": "João", "NPS": 75.2, "Vendas": 29}
    ]
    
    gerador = PDFGeneratorAdaptativo()
    
    print("\n📋 Teste 1: Dados estruturados")
    gerador.gerar_pdf_adaptativo(exemplo_estruturado, "Teste_Estruturado")
    
    print("\n📋 Teste 2: Texto IA")
    gerador.gerar_pdf_adaptativo(exemplo_texto, "Teste_Texto")
    
    print("\n📋 Teste 3: Dicionário")
    gerador.gerar_pdf_adaptativo(exemplo_dict, "Teste_Dict")
    
    print("\n📋 Teste 4: Tabela")
    gerador.gerar_pdf_adaptativo(exemplo_tabela, "Teste_Tabela")
    
    print("\n✅ Todos os testes concluídos!")
    print("📁 Verifique a pasta 'relatorios/' para os PDFs gerados")
    
    # Teste da função de conveniência
    print("\n🔧 Testando função de conveniência...")
    gerar_pdf_inteligente("NPS geral: 82.3%\n✅ Ótimo resultado este mês!", "Conveniencia")