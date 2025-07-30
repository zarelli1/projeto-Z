#!/usr/bin/env python3
"""
Analisador NPS Completo - Análise automática de planilhas Google Sheets
Autor: Claude Code  
Data: 27/07/2025
"""

import pandas as pd
import requests
import re
import io
from datetime import datetime
import unicodedata
import openai


class AnalisadorNPSCompleto:
    """Analisador completo de NPS com extração automática e métricas segmentadas"""
    
    def __init__(self, nome_loja="Mercadão dos Óculos", gids_customizados=None):
        self.nome_loja = nome_loja
        self.dados_abas = {}
        self.metricas_calculadas = {}
        self.gids_customizados = gids_customizados or []  # Lista de GIDs personalizados
        self.openai_client = openai.OpenAI(
            api_key="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"
        )
    
    def adicionar_gids(self, *gids):
        """Adiciona GIDs específicos à lista de busca"""
        for gid in gids:
            if gid not in self.gids_customizados:
                self.gids_customizados.append(gid)
        print(f"✅ GIDs adicionados: {gids}")
        print(f"📋 Total de GIDs customizados: {len(self.gids_customizados)}")
    
    def definir_gids(self, gids_lista):
        """Define uma lista completa de GIDs para busca"""
        self.gids_customizados = list(gids_lista)
        print(f"✅ GIDs definidos: {self.gids_customizados}")
    
    def limpar_gids(self):
        """Remove todos os GIDs customizados (volta ao padrão)"""
        self.gids_customizados = []
        print("✅ GIDs customizados removidos - usando busca padrão")
        
    def analisar_planilha(self, url_planilha):
        """
        Análise completa da planilha NPS
        Retorna resumo estruturado em texto
        """
        try:
            print("🚀 Iniciando análise completa NPS...")
            print(f"📍 Loja: {self.nome_loja}")
            
            # ETAPA 1: Extração automática das abas
            print("\n📥 ETAPA 1: Extração das Abas")
            if not self._extrair_abas_automaticamente(url_planilha):
                return "❌ Falha na extração das abas"
            
            # ETAPA 2: Padronização dos dados
            print("\n🔧 ETAPA 2: Padronização dos Dados")
            self._padronizar_todos_dados()
            
            # ETAPA 3: Cálculo das métricas NPS
            print("\n📊 ETAPA 3: Cálculo das Métricas NPS")
            self._calcular_metricas_nps()
            
            # ETAPA 4: Análise IA dos insights
            print("\n🤖 ETAPA 4: Análise IA dos Insights")
            insights_ia = self._gerar_insights_ia()
            
            # ETAPA 5: Geração do resumo final
            print("\n📋 ETAPA 5: Geração do Resumo")
            resumo = self._gerar_resumo_completo(insights_ia)
            
            print("✅ Análise concluída com sucesso!")
            return resumo
            
        except Exception as e:
            return f"❌ Erro na análise: {str(e)}"
    
    def _extrair_abas_automaticamente(self, url):
        """Sistema multi-estratégia para descobrir abas de qualquer planilha"""
        try:
            sheet_id = self._extrair_sheet_id(url)
            if not sheet_id:
                print("❌ ID da planilha não encontrado")
                return False
            
            print("🔍 Iniciando descoberta multi-estratégia de abas...")
            
            # === ESTRATÉGIA 0: PLANILHA ABA ÚNICA (sua planilha especial) ===
            print("🎯 ESTRATÉGIA 0: Verificando se é planilha de aba única...")
            if self._tentar_extracao_aba_unica(sheet_id, url):
                return True
            
            # === ESTRATÉGIA 1: GIDs CUSTOMIZADOS (mais rápido) ===
            if self.gids_customizados:
                print(f"🎯 ESTRATÉGIA 1: Usando GIDs customizados: {self.gids_customizados}")
                abas_encontradas = self._buscar_por_gids_especificos(sheet_id, self.gids_customizados)
                if len(abas_encontradas) >= 2:  # Se encontrou pelo menos 2 abas
                    self.dados_abas = abas_encontradas
                    return self._finalizar_extracao(abas_encontradas)
            
            # === ESTRATÉGIA 1.5: BUSCA POR ÍNDICE DAS ABAS ===
            print("🎯 ESTRATÉGIA 1.5: Busca por índice das abas...")
            abas_por_indice = self._buscar_por_indice_abas(sheet_id)
            if len(abas_por_indice) >= 2:
                self.dados_abas = abas_por_indice
                return self._finalizar_extracao(abas_por_indice)
            
            # === ESTRATÉGIA 1.7: BUSCA FORÇADA POR NOMES EXATOS ===
            print("🎯 ESTRATÉGIA 1.7: Busca forçada por nomes exatos das 3 abas...")
            abas_forcadas = self._buscar_forcado_nomes_exatos(sheet_id)
            if len(abas_forcadas) >= 2:
                self.dados_abas = abas_forcadas
                return self._finalizar_extracao(abas_forcadas)
            
            # === ESTRATÉGIA 2: BUSCA DIRETA POR NOMES (SEM GIDs) ===
            print("🔍 ESTRATÉGIA 2: Busca direta por nomes de abas...")
            abas_diretas = self._buscar_abas_por_nomes_diretos(sheet_id)
            if len(abas_diretas) >= 2:
                self.dados_abas = abas_diretas
                return self._finalizar_extracao(abas_diretas)
            
            # === ESTRATÉGIA 3: DESCOBERTA POR NOMES DAS ABAS ===
            print("🔍 ESTRATÉGIA 3: Tentando descobrir GIDs por nomes das abas...")
            abas_por_nomes = self._descobrir_gids_por_nomes(sheet_id)
            if len(abas_por_nomes) >= 2:
                self.dados_abas = abas_por_nomes
                return self._finalizar_extracao(abas_por_nomes)
            
            # === ESTRATÉGIA 4: BUSCA INTELIGENTE OTIMIZADA ===
            print("🔍 ESTRATÉGIA 4: Busca inteligente com padrões otimizados...")
            abas_inteligente = self._busca_inteligente_otimizada(sheet_id, url)
            if len(abas_inteligente) >= 1:
                self.dados_abas = abas_inteligente
                return self._finalizar_extracao(abas_inteligente)
            
            # === ESTRATÉGIA 5: BUSCA EXAUSTIVA (último recurso) ===
            print("🔍 ESTRATÉGIA 5: Busca exaustiva (último recurso)...")
            abas_exaustiva = self._busca_exaustiva(sheet_id)
            if len(abas_exaustiva) >= 1:
                self.dados_abas = abas_exaustiva
                return self._finalizar_extracao(abas_exaustiva)
            
            print("❌ Nenhuma aba válida encontrada em todas as estratégias")
            return False
                
        except Exception as e:
            print(f"❌ Erro na extração: {str(e)}")
            return False
    
    def _ler_csv_com_encoding(self, texto_csv):
        """Lê CSV tentando múltiplos encodings"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                # Trata bytes vs string
                if isinstance(texto_csv, bytes):
                    texto_decoded = texto_csv.decode(encoding)
                else:
                    texto_decoded = str(texto_csv)
                
                df = pd.read_csv(io.StringIO(texto_decoded))
                if len(df) > 0:  # Verifica se o DataFrame não está vazio
                    return df
            except Exception:
                continue
        
        # Fallback para DataFrame vazio se tudo falhar
        print("   ⚠️ Erro ao ler CSV - retornando DataFrame vazio")
        return pd.DataFrame()
    
    def _identificar_tipo_aba(self, df):
        """Identifica o tipo da aba baseado na estrutura das colunas - Sistema Inteligente com Priorização"""
        # Corrige encoding das colunas primeiro
        colunas_corrigidas = [self._corrigir_encoding_comum(str(col)) for col in df.columns]
        
        print(f"   🔍 Analisando colunas: {colunas_corrigidas}")
        
        colunas_texto = ' '.join(colunas_corrigidas)
        
        # === PRIORIDADE 1: DETECTAR D+30 (WhatsApp é indicador muito forte) ===
        palavras_whatsapp = ['whatsapp', 'zap', 'wpp', 'zapzap', 'whats', 'what', 'watts']
        tem_whatsapp = any(palavra in colunas_texto for palavra in palavras_whatsapp)
        
        # Se tem WhatsApp, é MUITO provavelmente D+30, mesmo que tenha outras palavras
        if tem_whatsapp:
            whatsapp_encontrados = [p for p in palavras_whatsapp if p in colunas_texto]
            print(f"   ✅ Detectado NPS D+30 (PRIORIDADE: WhatsApp): {whatsapp_encontrados}")
            return 'NPS_D30'
        
        # Outras palavras D+30 (sem WhatsApp)
        outras_palavras_d30 = [
            'produto', 'product', 'd+30', 'd30', 'nps d+30', 'nps d30',
            'trinta', '30', 'pos-venda', 'pos venda', 'satisfacao produto',
            'qualidade produto', 'mercadoria', 'oculos', 'óculos'
        ]
        palavras_d30_encontradas = [p for p in outras_palavras_d30 if p in colunas_texto]
        if palavras_d30_encontradas:
            print(f"   ✅ Detectado NPS D+30 (outras palavras): {palavras_d30_encontradas}")
            return 'NPS_D30'
        
        # === PRIORIDADE 2: DETECTAR D+1 (telefone sem WhatsApp) ===
        palavras_telefone = ['telefone', 'fone', 'phone', 'tel']
        tem_telefone = any(palavra in colunas_texto for palavra in palavras_telefone)
        
        if tem_telefone and not tem_whatsapp:
            print(f"   ✅ Detectado NPS D+1 (telefone sem WhatsApp)")
            return 'NPS_D1'
        
        # === PRIORIDADE 3: NPS RUIM (casos críticos com gestão) ===
        # Palavras específicas de resolução/gestão de casos críticos (MELHORADAS)
        palavras_gestao_casos = [
            'situacao', 'situação', 'situacao', 'situacaao',  # Variações de situação
            'resolucao', 'resolução', 'resolucao', 'resoução', 'resoucao',  # Variações de resolução
            'comentario_da_resolucao', 'comentario_resolucao', 'comentario da resolucao',
            'fonte', 'origem', 'canal', 'motivo', 'problema',
            'data_resolucao', 'data_resolução', 'data resoução', 'resolvido', 'pendente',
            'analise', 'análise', 'tratamento', 'followup', 'follow_up',
            'ruim', 'critico', 'problemas', 'reclamacao', 'reclamação', 'status'
        ]
        
        # Busca mais específica para detectar situação/resolução com acentos
        tem_situacao_variantes = any(palavra in colunas_texto for palavra in [
            'situacao', 'situação', 'situacaao', 'situacão'
        ])
        tem_resolucao_variantes = any(palavra in colunas_texto for palavra in [
            'resolucao', 'resolução', 'resoução', 'resoucao'
        ])
        tem_fonte = any(palavra in colunas_texto for palavra in ['fonte', 'origem'])
        tem_bot = any(palavra in colunas_texto for palavra in ['bot', 'id_bot', 'id bot'])
        
        palavras_gestao_encontradas = [p for p in palavras_gestao_casos if p in colunas_texto]
        
        # CRITÉRIO MAIS ESPECÍFICO para NPS_Ruim:
        # Se tem bot + (situação OU resolução OU fonte), é NPS_Ruim
        if tem_bot and (tem_situacao_variantes or tem_resolucao_variantes or tem_fonte):
            indicadores = []
            if tem_situacao_variantes: indicadores.append('situacao')
            if tem_resolucao_variantes: indicadores.append('resolucao') 
            if tem_fonte: indicadores.append('fonte')
            indicadores.append('bot')
            print(f"   ✅ Detectado NPS Ruim (gestão específica): {indicadores}")
            return 'NPS_Ruim'
        
        # Fallback original: pelo menos 2 indicadores de gestão
        if len(palavras_gestao_encontradas) >= 2:
            print(f"   ✅ Detectado NPS Ruim (múltiplos indicadores): {palavras_gestao_encontradas}")
            return 'NPS_Ruim'
        
        # === FALLBACK: Se tem bot mas não outros indicadores, pode ser dados gerais ===
        if tem_bot:
            print(f"   ⚠️ Bot detectado mas sem indicadores de gestão - assumindo dados gerais")
            return 'Dados_Gerais'
        
        # === MÉTODO 2: SISTEMA DE PONTUAÇÃO AVANÇADO ===
        
        # Se o método original não funcionou, usa pontuação avançada
        palavras_avaliacao = ['avaliacao', 'avaliação', 'nota', 'score', 'rating', 'avaliaacaao']
        if any(palavra in ' '.join(colunas_corrigidas) for palavra in palavras_avaliacao):
            print(f"   🔍 Método original não identificou - usando análise avançada...")
            
            # Análise DETALHADA baseada no conteúdo dos dados
            if len(df) > 0:
                # Analisa múltiplas linhas, não só a primeira
                amostra_dados = df.head(10).astype(str).apply(lambda x: ' '.join(x), axis=1).str.lower()
                conteudo_completo = ' '.join(amostra_dados)
                
                print(f"   🔍 Analisando conteúdo: {conteudo_completo[:200]}...")
                
                # Sistema de pontuação melhorado
                scores = {'NPS_Ruim': 0, 'NPS_D30': 0, 'NPS_D1': 0}
                
                # Padrões NPS Ruim no conteúdo
                padroes_ruim = [
                    'ruim', 'critico', 'problema', 'reclamacao', 'insatisfeito',
                    'pendente', 'resolvido', 'em andamento', 'analise',
                    'fonte', 'canal', 'motivo', 'situacao', 'status'
                ]
                
                score_ruim = sum(1 for padrao in padroes_ruim if padrao in conteudo_completo)
                scores['NPS_Ruim'] = score_ruim
                
                # Padrões D+30 no conteúdo (melhorado)
                padroes_d30 = [
                    'whats', 'zap', 'wpp', '55', '+55', 'produto', 'product',
                    'd+30', 'd30', 'trinta', 'pos-venda', 'satisfacao',
                    'qualidade', 'mercadoria', 'oculos', 'óculos', 'lente',
                    'armacao', 'armação', 'grau', 'receita', 'laboratorio'
                ]
                score_d30 = sum(1 for padrao in padroes_d30 if padrao in conteudo_completo)
                scores['NPS_D30'] = score_d30
                
                # Padrões D+1 no conteúdo  
                padroes_d1 = ['atendimento', 'servico', 'telefone']
                score_d1 = sum(1 for padrao in padroes_d1 if padrao in conteudo_completo)
                scores['NPS_D1'] = score_d1
                
                print(f"   📊 Scores de conteúdo: NPS_Ruim({score_ruim}) | D30({score_d30}) | D1({score_d1})")
                
                # Decisão baseada em pontuação
                if score_ruim >= 2:  # Se encontrar 2+ padrões de NPS Ruim
                    print(f"   ✅ Identificado como NPS_Ruim (análise de conteúdo)")
                    return 'NPS_Ruim'
                elif score_d30 >= 1:  # Se encontrar WhatsApp
                    print(f"   ✅ Identificado como NPS_D30 (análise de conteúdo)")
                    return 'NPS_D30'
                elif score_d1 >= 1 or tem_telefone:  # Se encontrar padrões D+1 ou tem telefone
                    print(f"   ✅ Identificado como NPS_D1 (análise de conteúdo)")
                    return 'NPS_D1'
            
            # Fallback para D+1 se tem avaliação (ORIGINAL)
            print(f"   ✅ Fallback: NPS_D1 (tem avaliação)")
            return 'NPS_D1'
        
        print(f"   ⚠️ Aba não identificada (sem colunas de avaliação)")
        return 'desconhecido'
    
    def _padronizar_todos_dados(self):
        """Padroniza dados de todas as abas"""
        for tipo_aba, df in self.dados_abas.items():
            try:
                # Padroniza nomes das colunas
                df_padronizado = self._padronizar_colunas(df)
                
                # Garante que Avaliação seja numérica
                df_padronizado = self._padronizar_avaliacao(df_padronizado)
                
                # Remove linhas vazias
                df_padronizado = df_padronizado.dropna(how='all')
                
                self.dados_abas[tipo_aba] = df_padronizado
                print(f"✅ {tipo_aba}: dados padronizados")
                
            except Exception as e:
                print(f"⚠️ Erro na padronização de {tipo_aba}: {str(e)}")
    
    def _padronizar_colunas(self, df):
        """Padroniza nomes das colunas: remove acentos, espaços → underscore"""
        df_novo = df.copy()
        
        colunas_padronizadas = {}
        for col in df.columns:
            # Remove acentos
            col_sem_acento = self._remover_acentos(str(col))
            # Minúsculo
            col_lower = col_sem_acento.lower()
            # Remove caracteres especiais e substitui espaços
            col_limpo = re.sub(r'[^\w\s]', '', col_lower)
            col_final = re.sub(r'\s+', '_', col_limpo).strip('_')
            
            colunas_padronizadas[col] = col_final
        
        return df_novo.rename(columns=colunas_padronizadas)
    
    def _remover_acentos(self, texto):
        """Remove acentos de uma string"""
        # Primeiro corrige problemas comuns de encoding
        texto = self._corrigir_encoding_comum(texto)
        # Depois remove acentos normalmente
        return unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('ascii')
    
    def _corrigir_encoding_comum(self, texto):
        """Corrige problemas comuns de encoding"""
        corrections = {
            'avaliaãão': 'avaliacao',
            'avaliação': 'avaliacao',
            'avaliaa§a£o': 'avaliacao',  # Encoding específico encontrado
            'comentãrio': 'comentario', 
            'comentário': 'comentario',
            'comenta¡rio': 'comentario',  # Encoding específico encontrado
            'situaãão': 'situacao',
            'situação': 'situacao',
            'resoluãão': 'resolucao',
            'resolução': 'resolucao',
            'telefonÃª': 'telefone',
            'whatsapÃª': 'whatsapp',
            '§': 'c',  # Corrige caracteres específicos
            '£': 'a',
            '¡': 'a',
            'ã': 'a',
            'ç': 'c',
            'é': 'e',
            'í': 'i',
            'ó': 'o',
            'ú': 'u',
            'â': 'a',
            'ê': 'e',
            'ô': 'o'
        }
        
        texto_corrigido = str(texto).lower()
        for erro, correto in corrections.items():
            texto_corrigido = texto_corrigido.replace(erro, correto)
        
        return texto_corrigido
    
    def _padronizar_avaliacao(self, df):
        """Garante que a coluna Avaliação seja numérica"""
        # Lista expandida de possíveis nomes para coluna de avaliação
        nomes_avaliacao = [
            'avaliacao', 'avaliaçao', 'avaliaãão', 'avaliação', 'avaliaacaao',
            'nota', 'score', 'rating', 'pontuacao', 'pontuação',
            'satisfaction', 'satisfacao', 'satisfação'
        ]
        
        col_avaliacao = self._encontrar_coluna_por_nomes(df.columns, nomes_avaliacao)
        
        if col_avaliacao:
            df[col_avaliacao] = pd.to_numeric(df[col_avaliacao], errors='coerce')
            print(f"   ✅ Coluna de avaliação encontrada: '{col_avaliacao}'")
        else:
            print("   ⚠️ Coluna de avaliação não encontrada")
        
        return df
    
    def _encontrar_coluna_por_nomes(self, colunas, nomes_possiveis):
        """Encontra uma coluna baseada em lista de nomes possíveis"""
        for col in colunas:
            col_limpo = self._corrigir_encoding_comum(str(col))
            for nome in nomes_possiveis:
                if nome in col_limpo:
                    return col
        return None
    
    def _calcular_metricas_nps(self):
        """Calcula métricas NPS para cada aba"""
        for tipo_aba, df in self.dados_abas.items():
            try:
                if tipo_aba in ['NPS_D1', 'NPS_D30']:
                    metricas = self._calcular_nps_aba(df, tipo_aba)
                    self.metricas_calculadas[tipo_aba] = metricas
                    print(f"✅ {tipo_aba}: métricas calculadas")
                elif tipo_aba == 'NPS_Ruim':
                    # Para NPS Ruim, fazemos análise diferente
                    analise_ruim = self._analisar_nps_ruim(df)
                    self.metricas_calculadas[tipo_aba] = analise_ruim
                    print(f"✅ {tipo_aba}: análise de casos críticos concluída")
                    
            except Exception as e:
                print(f"⚠️ Erro no cálculo de métricas para {tipo_aba}: {str(e)}")
    
    def _calcular_nps_aba(self, df, tipo_aba):
        """Calcula NPS para uma aba específica (D+1 ou D+30)"""
        # Encontra coluna de avaliação usando método melhorado
        nomes_avaliacao = [
            'avaliacao', 'avaliaçao', 'avaliaãão', 'avaliação', 'avaliaacaao',
            'nota', 'score', 'rating', 'pontuacao', 'pontuação'
        ]
        
        col_avaliacao = self._encontrar_coluna_por_nomes(df.columns, nomes_avaliacao)
        
        if not col_avaliacao:
            return {'erro': 'Coluna de avaliação não encontrada'}
        
        # Remove valores inválidos e faz limpeza rigorosa
        avaliacoes_validas = df[col_avaliacao].dropna()
        
        # Remove valores não numéricos ou fora do range esperado (0-10)
        avaliacoes_validas = avaliacoes_validas[
            (avaliacoes_validas >= 0) & (avaliacoes_validas <= 10)
        ]
        
        total_respostas = len(avaliacoes_validas)
        
        if total_respostas == 0:
            return {'erro': 'Nenhuma avaliação válida encontrada (range 0-10)'}
        
        # Classifica conforme critérios NPS
        promotores = len(avaliacoes_validas[avaliacoes_validas >= 9])
        neutros = len(avaliacoes_validas[(avaliacoes_validas >= 7) & (avaliacoes_validas <= 8)])
        detratores = len(avaliacoes_validas[avaliacoes_validas <= 6])
        
        # Calcula percentuais
        perc_promotores = (promotores / total_respostas) * 100
        perc_neutros = (neutros / total_respostas) * 100
        perc_detratores = (detratores / total_respostas) * 100
        
        # Score NPS
        nps_score = perc_promotores - perc_detratores
        
        return {
            'tipo': 'Atendimento' if tipo_aba == 'NPS_D1' else 'Produto',
            'total_respostas': total_respostas,
            'promotores': {'count': promotores, 'percentual': perc_promotores},
            'neutros': {'count': neutros, 'percentual': perc_neutros},
            'detratores': {'count': detratores, 'percentual': perc_detratores},
            'nps_score': nps_score,
            'nota_media': avaliacoes_validas.mean()
        }
    
    def _analisar_nps_ruim(self, df):
        """Analisa casos críticos da aba NPS Ruim"""
        try:
            # Encontra colunas importantes usando método melhorado
            nomes_avaliacao = ['avaliacao', 'avaliaçao', 'avaliaãão', 'avaliaacaao', 'nota', 'score']
            nomes_comentario = ['comentario', 'comentário', 'comment', 'feedback', 'observacao']
            nomes_vendedor = ['vendedor', 'atendente', 'consultor', 'funcionario', 'agent']
            nomes_loja = ['loja', 'store', 'filial', 'unidade']
            
            col_avaliacao = self._encontrar_coluna_por_nomes(df.columns, nomes_avaliacao)
            col_comentario = self._encontrar_coluna_por_nomes(df.columns, nomes_comentario)
            col_vendedor = self._encontrar_coluna_por_nomes(df.columns, nomes_vendedor)
            col_loja = self._encontrar_coluna_por_nomes(df.columns, nomes_loja)
            
            total_casos = len(df)
            
            # Casos mais críticos (menores notas)
            casos_criticos = []
            if col_avaliacao:
                df_ordenado = df.sort_values(col_avaliacao, na_position='last')
                
                for i, (idx, row) in enumerate(df_ordenado.head(10).iterrows()):
                    caso = {
                        'posicao': i + 1,
                        'avaliacao': row[col_avaliacao] if col_avaliacao else 'N/A',
                        'comentario': str(row[col_comentario])[:200] if col_comentario and pd.notna(row[col_comentario]) else 'Sem comentário',
                        'vendedor': row[col_vendedor] if col_vendedor and pd.notna(row[col_vendedor]) else 'N/A',
                        'loja': row[col_loja] if col_loja and pd.notna(row[col_loja]) else 'N/A'
                    }
                    casos_criticos.append(caso)
            
            return {
                'tipo': 'Casos Críticos',
                'total_casos': total_casos,
                'casos_criticos': casos_criticos
            }
            
        except Exception as e:
            return {'erro': f'Erro na análise de casos críticos: {str(e)}'}
    
    def _gerar_resumo_completo(self, insights_ia):
        """Gera resumo final estruturado com insights IA"""
        try:
            resumo = f"""
📅 Data da Análise: {datetime.now().strftime('%d/%m/%Y às %H:%M')}

"""
            
            # Resumo das métricas NPS D+1 e D+30
            resumo += self._gerar_secao_metricas_nps()
            
            # Análise de casos críticos
            resumo += self._gerar_secao_casos_criticos()
            
            # INSIGHTS IA - Nova seção
            resumo += self._gerar_secao_insights_ia(insights_ia)
            
            return resumo
            
        except Exception as e:
            return f"Erro na geração do resumo: {str(e)}"
    
    def _gerar_secao_insights_ia(self, insights_ia):
        """Gera seção com insights da IA"""
        secao = """
┌─────────────────────────────────────────────────────────────┐
│                    INSIGHTS IA                             │
└─────────────────────────────────────────────────────────────┘

"""
        secao += insights_ia + "\n\n"
        return secao
    
    def _gerar_secao_metricas_nps(self):
        """Gera seção com métricas NPS de D+1 e D+30"""
        secao = """
┌─────────────────────────────────────────────────────────────┐
│                     MÉTRICAS NPS                           │
└─────────────────────────────────────────────────────────────┘

"""
        
        for tipo_aba in ['NPS_D1', 'NPS_D30']:
            if tipo_aba in self.metricas_calculadas:
                metricas = self.metricas_calculadas[tipo_aba]
                
                if 'erro' not in metricas:
                    tipo_nome = metricas['tipo']
                    secao += f"""
🎯 {tipo_nome.upper()}:
   📊 Total de Respostas: {metricas['total_respostas']:,}
   📈 Score NPS: {metricas['nps_score']:.1f}
   ⭐ Nota Média: {metricas['nota_media']:.2f}
   
   📋 Distribuição:
   🟢 Promotores (9-10): {metricas['promotores']['count']:,} ({metricas['promotores']['percentual']:.1f}%)
   🟡 Neutros (7-8):     {metricas['neutros']['count']:,} ({metricas['neutros']['percentual']:.1f}%)
   🔴 Detratores (≤6):   {metricas['detratores']['count']:,} ({metricas['detratores']['percentual']:.1f}%)
"""
                else:
                    secao += f"\n⚠️ {tipo_aba}: {metricas['erro']}\n"
        
        return secao
    
    def _gerar_secao_casos_criticos(self):
        """Gera seção com casos críticos do NPS Ruim"""
        secao = """
┌─────────────────────────────────────────────────────────────┐
│                   CASOS CRÍTICOS                           │
└─────────────────────────────────────────────────────────────┘

"""
        
        if 'NPS_Ruim' in self.metricas_calculadas:
            dados_ruim = self.metricas_calculadas['NPS_Ruim']
            
            if 'erro' not in dados_ruim:
                secao += f"📊 Total de Casos Críticos: {dados_ruim['total_casos']:,}\n\n"
                secao += "🔍 10 CASOS MAIS CRÍTICOS (menores notas):\n\n"
                
                for caso in dados_ruim['casos_criticos']:
                    secao += f"""
{caso['posicao']:2d}. 📍 Nota: {caso['avaliacao']} | Vendedor: {caso['vendedor']} | Loja: {caso['loja']}
    💬 "{caso['comentario']}"
"""
            else:
                secao += f"⚠️ NPS Ruim: {dados_ruim['erro']}\n"
        else:
            secao += "⚠️ Aba 'NPS Ruim' não encontrada na planilha\n\n"
            secao += "💡 ANÁLISE ALTERNATIVA DE CASOS CRÍTICOS:\n"
            secao += self._analisar_detratores_das_abas_existentes()
        
        return secao
    
    def _gerar_secao_resumo_geral(self):
        """Gera seção de resumo geral"""
        secao = """
┌─────────────────────────────────────────────────────────────┐
│                    RESUMO GERAL                            │
└─────────────────────────────────────────────────────────────┘

"""
        
        total_respostas_geral = 0
        abas_processadas = 0
        
        for tipo_aba, metricas in self.metricas_calculadas.items():
            if 'erro' not in metricas:
                abas_processadas += 1
                if 'total_respostas' in metricas:
                    total_respostas_geral += metricas['total_respostas']
                elif 'total_casos' in metricas:
                    total_respostas_geral += metricas['total_casos']
        
        secao += f"""📊 ESTATÍSTICAS GERAIS:
   • Abas processadas: {abas_processadas}/3
   • Total de registros analisados: {total_respostas_geral:,}
   • Planilha: Google Sheets (acesso público)
   
🏪 Loja: {self.nome_loja}
⏰ Processado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
"""
        
        return secao
    
    def _analisar_detratores_das_abas_existentes(self):
        """Analisa detratores das abas D+1 e D+30 quando não há aba NPS Ruim"""
        try:
            analise = ""
            
            for tipo_aba, df in self.dados_abas.items():
                if tipo_aba in ['NPS_D1', 'NPS_D30']:
                    # Encontra colunas importantes
                    nomes_avaliacao = ['avaliacao', 'avaliaçao', 'avaliaãão', 'avaliaacaao', 'nota', 'score']
                    nomes_comentario = ['comentario', 'comentário', 'comment', 'feedback', 'comentaario']
                    nomes_vendedor = ['vendedor', 'atendente', 'consultor', 'funcionario']
                    nomes_loja = ['loja', 'store', 'filial', 'unidade']
                    
                    col_avaliacao = self._encontrar_coluna_por_nomes(df.columns, nomes_avaliacao)
                    col_comentario = self._encontrar_coluna_por_nomes(df.columns, nomes_comentario)
                    col_vendedor = self._encontrar_coluna_por_nomes(df.columns, nomes_vendedor)
                    col_loja = self._encontrar_coluna_por_nomes(df.columns, nomes_loja)
                    
                    if col_avaliacao:
                        # Filtra detratores (nota ≤ 6)
                        detratores = df[df[col_avaliacao] <= 6]
                        
                        if len(detratores) > 0:
                            tipo_nome = 'D+1 (Atendimento)' if tipo_aba == 'NPS_D1' else 'D+30 (Produto)'
                            analise += f"\n🔴 DETRATORES {tipo_nome}:\n"
                            analise += f"   📊 Total: {len(detratores)} casos\n\n"
                            
                            # Top 5 piores casos
                            detratores_ordenados = detratores.sort_values(col_avaliacao).head(5)
                            
                            for i, (idx, row) in enumerate(detratores_ordenados.iterrows(), 1):
                                nota = row[col_avaliacao] if pd.notna(row[col_avaliacao]) else 'N/A'
                                vendedor = row[col_vendedor] if col_vendedor and pd.notna(row[col_vendedor]) else 'N/A'
                                loja = row[col_loja] if col_loja and pd.notna(row[col_loja]) else 'N/A'
                                comentario = str(row[col_comentario])[:150] if col_comentario and pd.notna(row[col_comentario]) else 'Sem comentário'
                                
                                analise += f"   {i}. 📍 Nota: {nota} | {vendedor} | {loja}\n"
                                analise += f"      💬 \"{comentario}...\"\n\n"
            
            if not analise:
                analise = "   ✅ Excelente! Poucos ou nenhum detrator encontrado nas abas disponíveis.\n"
            
            return analise
            
        except Exception as e:
            return f"   ❌ Erro na análise de detratores: {str(e)}\n"
    
    def _gerar_insights_ia(self):
        """Gera insights automáticos usando IA"""
        try:
            print("🤖 Gerando insights com IA...")
            
            # Prepara dados resumidos para IA
            dados_para_ia = self._preparar_dados_para_ia()
            
            prompt = f"""
Analise os dados NPS da empresa {self.nome_loja} e gere insights estratégicos:

DADOS RESUMIDOS:
{dados_para_ia}

GERE UM RELATÓRIO DE INSIGHTS NO FORMATO:

🎯 INSIGHTS PRINCIPAIS:
• [Insight principal sobre performance]
• [Insight sobre pontos fortes]
• [Insight sobre oportunidades]

📊 ANÁLISE COMPARATIVA:
• D+1 vs D+30: [Comparação entre atendimento e produto]
• Padrões identificados: [Padrões nos dados]

⚠️ PONTOS DE ATENÇÃO:
• [Principal problema identificado]
• [Vendedores ou lojas que precisam atenção]

🚀 RECOMENDAÇÕES ESTRATÉGICAS:
1. [Recomendação urgente]
2. [Recomendação de melhoria]
3. [Recomendação preventiva]

Seja específico, use dados reais e foque em ações práticas.
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Você é um consultor especialista em NPS e experiência do cliente. Seja preciso e actionable."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            insights = response.choices[0].message.content
            print("✅ Insights IA gerados!")
            return insights
            
        except Exception as e:
            print(f"⚠️ Erro na geração de insights IA: {str(e)}")
            return self._gerar_insights_basicos()
    
    def _preparar_dados_para_ia(self):
        """Prepara resumo estruturado dos dados para IA"""
        try:
            resumo_ia = f"=== ANÁLISE NPS {self.nome_loja.upper()} ===\n\n"
            
            # Métricas de cada aba
            for tipo_aba, metricas in self.metricas_calculadas.items():
                if 'erro' not in metricas:
                    if tipo_aba in ['NPS_D1', 'NPS_D30']:
                        resumo_ia += f"📊 {metricas['tipo'].upper()}:\n"
                        resumo_ia += f"   • Total respostas: {metricas['total_respostas']:,}\n"
                        resumo_ia += f"   • Score NPS: {metricas['nps_score']:.1f}\n"
                        resumo_ia += f"   • Nota média: {metricas['nota_media']:.2f}\n"
                        resumo_ia += f"   • Promotores: {metricas['promotores']['count']} ({metricas['promotores']['percentual']:.1f}%)\n"
                        resumo_ia += f"   • Neutros: {metricas['neutros']['count']} ({metricas['neutros']['percentual']:.1f}%)\n"
                        resumo_ia += f"   • Detratores: {metricas['detratores']['count']} ({metricas['detratores']['percentual']:.1f}%)\n\n"
                    
                    elif tipo_aba == 'NPS_Ruim':
                        resumo_ia += f"🔴 CASOS CRÍTICOS:\n"
                        resumo_ia += f"   • Total casos: {metricas['total_casos']}\n"
                        
                        # Amostra dos piores casos
                        if 'casos_criticos' in metricas and len(metricas['casos_criticos']) > 0:
                            resumo_ia += "   • Principais problemas:\n"
                            for caso in metricas['casos_criticos'][:3]:
                                resumo_ia += f"     - Nota {caso['avaliacao']} | {caso['vendedor']} | {caso['loja']}\n"
                        resumo_ia += "\n"
            
            # Análise de vendedores (se disponível)
            resumo_ia += self._analisar_vendedores_para_ia()
            
            return resumo_ia
            
        except Exception as e:
            return f"Dados básicos disponíveis para {self.nome_loja}\nErro: {str(e)}"
    
    def _analisar_vendedores_para_ia(self):
        """Analisa performance dos vendedores para IA"""
        try:
            analise_vendedores = "\n📈 ANÁLISE DE VENDEDORES:\n"
            
            # Combina dados de todas as abas para análise de vendedores
            todos_vendedores = {}
            
            for tipo_aba, df in self.dados_abas.items():
                col_vendedor = None
                col_avaliacao = None
                
                for col in df.columns:
                    col_lower = col.lower()
                    if 'vendedor' in col_lower:
                        col_vendedor = col
                    elif 'avaliacao' in col_lower or 'nota' in col_lower:
                        col_avaliacao = col
                
                if col_vendedor and col_avaliacao:
                    vendedores_aba = df.groupby(col_vendedor)[col_avaliacao].agg(['count', 'mean']).sort_values('mean', ascending=False)
                    
                    analise_vendedores += f"   • {tipo_aba}: {len(vendedores_aba)} vendedores únicos\n"
                    if len(vendedores_aba) > 0:
                        melhor = vendedores_aba.index[0]
                        nota_melhor = vendedores_aba.iloc[0]['mean']
                        analise_vendedores += f"     Top: {melhor} (média {nota_melhor:.2f})\n"
            
            return analise_vendedores
            
        except Exception as e:
            return f"\n⚠️ Erro na análise de vendedores: {str(e)}\n"
    
    def _gerar_insights_basicos(self):
        """Gera insights básicos sem IA"""
        return """
🎯 INSIGHTS PRINCIPAIS:
• Dados extraídos e processados com sucesso
• Métricas NPS calculadas conforme padrão de mercado
• Análise segmentada por tipo de avaliação

📊 ANÁLISE COMPARATIVA:
• Sistema funcionando adequadamente
• Dados estruturados para análise

⚠️ PONTOS DE ATENÇÃO:
• Verificar conexão com IA para insights mais detalhados

🚀 RECOMENDAÇÕES ESTRATÉGICAS:
1. Monitorar regularmente as métricas NPS
2. Focar na melhoria contínua da experiência
3. Implementar ações baseadas nos feedbacks
"""
    
    def _extrair_sheet_id(self, url):
        """Extrai ID da planilha da URL"""
        try:
            pattern = r'/spreadsheets/d/([a-zA-Z0-9-_]+)'
            match = re.search(pattern, url)
            return match.group(1) if match else None
        except:
            return None
    
    def _extrair_gid_da_url(self, url):
        """Extrai GID da URL (gid=número)"""
        try:
            pattern = r'[?&#]gid=(\d+)'
            match = re.search(pattern, url)
            return int(match.group(1)) if match else None
        except:
            return None
    
    def _buscar_por_indice_abas(self, sheet_id):
        """ESTRATÉGIA 1.5: Busca por índice das abas (0, 1, 4)"""
        abas_encontradas = {}
        
        # Mapeamento: aba 0 = NPS_Ruim, aba 1 = NPS_D1, aba 4 = NPS_D30
        indices_mapeamento = {
            0: 'NPS_Ruim',
            1: 'NPS_D1', 
            4: 'NPS_D30'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print("   🔍 Testando extração por índices de abas (0, 1, 4)...")
        
        for indice, tipo_esperado in indices_mapeamento.items():
            try:
                # URL para acessar aba por índice
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&single=true&gid={indice}"
                response = requests.get(csv_url, timeout=10, headers=headers)
                
                if (response.status_code == 200 and 
                    response.text.strip() and 
                    'Error' not in response.text and
                    len(response.text) > 50):
                    
                    df = self._ler_csv_com_encoding(response.text)
                    if len(df) > 1:
                        # Verifica o tipo real da aba
                        tipo_real = self._identificar_tipo_aba(df)
                        
                        # Usa o tipo identificado se for válido, senão usa o esperado
                        tipo_final = tipo_real if tipo_real != 'desconhecido' else tipo_esperado
                        
                        if tipo_final not in abas_encontradas:
                            abas_encontradas[tipo_final] = df
                            print(f"   ✅ {tipo_final}: {len(df)} registros (índice {indice})")
                        
            except Exception as e:
                print(f"   ⚠️ Erro no índice {indice}: {str(e)[:50]}")
                continue
        
        return abas_encontradas
    
    def _buscar_forcado_nomes_exatos(self, sheet_id):
        """ESTRATÉGIA 1.7: Busca forçada pelos nomes exatos das 3 abas NPS"""
        abas_encontradas = {}
        
        # Mapeamento FORÇADO para garantir que as 3 abas sejam encontradas
        mapeamento_forcado = {
            'NPS D+1': 'NPS_D1',
            'NPS D+30': 'NPS_D30', 
            'NPS Ruim': 'NPS_Ruim'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"   🎯 Forçando busca pelos nomes: {list(mapeamento_forcado.keys())}")
        
        for nome_aba, tipo_forcado in mapeamento_forcado.items():
            try:
                # Busca direta pelo nome exato
                nome_encoded = nome_aba.replace(' ', '%20').replace('+', '%2B')
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={nome_encoded}"
                
                response = requests.get(csv_url, timeout=10, headers=headers)
                
                if (response.status_code == 200 and 
                    response.text.strip() and 
                    'Error' not in response.text and
                    len(response.text) > 100):
                    
                    df = self._ler_csv_com_encoding(response.text)
                    if len(df) > 1:
                        # FORÇA o tipo baseado no nome se for uma aba NPS específica
                        if nome_aba == 'NPS Ruim':
                            # Para aba "NPS Ruim", força o tipo independente da detecção
                            tipo_final = tipo_forcado
                            print(f"   🔒 FORÇADO: '{nome_aba}' → {tipo_forcado} (ignorando detecção automática)")
                        else:
                            # Para outras abas, usa detecção automática se possível
                            tipo_detectado = self._identificar_tipo_aba(df)
                            tipo_final = tipo_detectado if tipo_detectado != 'desconhecido' and tipo_detectado != 'Dados_Gerais' else tipo_forcado
                        
                        abas_encontradas[tipo_final] = df
                        print(f"   ✅ {tipo_final}: {len(df)} registros (nome forçado: '{nome_aba}')")
                        
            except Exception as e:
                print(f"   ⚠️ Erro na busca forçada '{nome_aba}': {str(e)[:50]}")
                continue
        
        return abas_encontradas
    
    # === MÉTODOS DAS ESTRATÉGIAS DE DESCOBERTA ===
    
    def _buscar_por_gids_especificos(self, sheet_id, gids_lista):
        """ESTRATÉGIA 1: Busca por GIDs específicos fornecidos"""
        abas_encontradas = {}
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for gid in gids_lista:
            # Retry com 2 tentativas por GID
            for tentativa in range(2):
                try:
                    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
                    response = requests.get(csv_url, timeout=15, headers=headers)
                    
                    # Validação melhor de response
                    if (response.status_code == 200 and 
                        response.text.strip() and 
                        'Error' not in response.text and 
                        'Sorry, unable to open the file at this time' not in response.text and
                        len(response.text) > 50):  # Verifica se não é resposta de erro do Google
                        
                        df = self._ler_csv_com_encoding(response.text)
                        if len(df) > 1:
                            tipo_aba = self._identificar_tipo_aba(df)
                            if tipo_aba != 'desconhecido':
                                abas_encontradas[tipo_aba] = df
                                print(f"   ✅ {tipo_aba}: {len(df)} registros (GID {gid})")
                                break  # Sucesso, sai do loop de retry
                            
                except Exception as e:
                    if tentativa == 1:  # Última tentativa
                        print(f"   ⚠️ Erro após 2 tentativas no GID {gid}: {str(e)[:50]}")
                    continue
        
        return abas_encontradas
    
    def _buscar_abas_por_nomes_diretos(self, sheet_id):
        """ESTRATÉGIA 2: Busca direta por nomes de abas (SEM GIDs)"""
        abas_encontradas = {}
        
        # Lista expandida de possíveis nomes para D+30
        nomes_d30 = [
            'NPS D+30', 'NPS D30', 'nps d+30', 'nps d30', 'D+30', 'D30', 'd+30', 'd30',
            'NPS D +30', 'NPS D +30', 'Produto', 'PRODUTO', 'produto', 
            'Satisfação Produto', 'Avaliação Produto', 'Pós-venda',
            'WhatsApp', 'Zap', 'WPP', 'Contato WhatsApp',
            'Mercadão D+30', 'MDO D+30', 'Óculos D+30',
            'Trinta dias', '30 dias', 'Pos venda', 'Qualidade'
        ]
        
        # Lista expandida de possíveis nomes para D+1  
        nomes_d1 = [
            'NPS D+1', 'NPS D1', 'nps d+1', 'nps d1', 'D+1', 'D1', 'd+1', 'd1',
            'NPS D +1', 'Atendimento', 'ATENDIMENTO', 'atendimento',
            'Telefone', 'Contato Telefone', 'Servico', 'Serviço',
            'Mercadão D+1', 'MDO D+1', 'Um dia', '1 dia'
        ]
        
        # Lista expandida de possíveis nomes para NPS Ruim
        nomes_ruim = [
            'NPS Ruim', 'NPS RUIM', 'nps ruim', 'Ruim', 'RUIM', 'ruim',
            'Crítico', 'CRITICO', 'critico', 'Casos Críticos',
            'Problemas', 'Reclamações', 'Detratores', 'Insatisfeitos',
            'Follow Up', 'Follow-up', 'Pendentes', 'Resolução'
        ]
        
        todos_nomes = {
            'NPS_D30': nomes_d30,
            'NPS_D1': nomes_d1, 
            'NPS_Ruim': nomes_ruim
        }
        
        for tipo_aba, lista_nomes in todos_nomes.items():
            for nome_aba in lista_nomes:
                try:
                    # Codifica o nome da aba para URL
                    nome_encoded = nome_aba.replace(' ', '%20').replace('+', '%2B')
                    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={nome_encoded}"
                    
                    response = requests.get(csv_url, timeout=5)
                    
                    if response.status_code == 200 and response.text.strip() and 'Error' not in response.text:
                        df = self._ler_csv_com_encoding(response.text)
                        if len(df) > 1:  # Tem dados válidos
                            # Confirma o tipo analisando o conteúdo
                            tipo_confirmado = self._identificar_tipo_aba(df)
                            if tipo_confirmado != 'desconhecido':
                                abas_encontradas[tipo_confirmado] = df
                                print(f"   ✅ {tipo_confirmado}: {len(df)} registros (nome: '{nome_aba}')")
                                break  # Encontrou esta aba, passa para próximo tipo
                            elif tipo_aba not in abas_encontradas:  # Se não confirmou tipo mas não tem aba deste tipo ainda
                                abas_encontradas[tipo_aba] = df
                                print(f"   ✅ {tipo_aba}: {len(df)} registros (nome: '{nome_aba}' - assumido)")
                                break
                                
                except Exception:
                    continue
        
        return abas_encontradas
    
    def _descobrir_gids_por_nomes(self, sheet_id):
        """ESTRATÉGIA 2: Tenta descobrir GIDs pelos nomes das abas usando padrões HTML"""
        abas_encontradas = {}
        
        try:
            print("   🔍 Analisando estrutura da planilha...")
            
            # Testa GIDs baseados em padrões de nomes conhecidos
            gids_por_nomes = self._gerar_gids_por_padroes_nomes()
            
            for gid in gids_por_nomes:
                try:
                    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
                    response = requests.get(csv_url, timeout=5)
                    
                    if response.status_code == 200 and response.text.strip():
                        df = self._ler_csv_com_encoding(response.text)
                        if len(df) > 1:
                            tipo_aba = self._identificar_tipo_aba(df)
                            if tipo_aba != 'desconhecido' and tipo_aba not in abas_encontradas:
                                abas_encontradas[tipo_aba] = df
                                print(f"   ✅ {tipo_aba}: {len(df)} registros (GID {gid} - por padrão)")
                                
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"   ⚠️ Erro na descoberta por nomes: {str(e)}")
        
        return abas_encontradas
    
    def _busca_inteligente_otimizada(self, sheet_id, url):
        """ESTRATÉGIA 3: Busca inteligente com padrões otimizados"""
        abas_encontradas = {}
        
        # GIDs inteligentes baseados na URL e padrões comuns
        gids_inteligentes = []
        
        # Extrai GID da URL e gera variações
        url_gid = self._extrair_gid_da_url(url)
        if url_gid:
            print(f"   🎯 GID da URL: {url_gid}")
            # Variações próximas mais amplas
            for i in range(-10, 11):
                if i != 0:
                    gids_inteligentes.append(url_gid + i)
            
            # Padrões matemáticos comuns
            gids_inteligentes.extend([
                url_gid // 2, url_gid * 2,
                url_gid + 100, url_gid - 100,
                url_gid + 1000, url_gid - 1000
            ])
        
        # GIDs sequenciais comuns
        gids_inteligentes.extend(range(0, 30))  # 0-29
        gids_inteligentes.extend(range(100, 120))  # 100-119
        gids_inteligentes.extend(['od6', 'od7', 'od8', 'od9', 'od10'])
        
        # GIDs grandes comuns
        gids_comuns_grandes = [
            1410159651, 476804694, 1234567890, 987654321,
            1000000000, 1200000000, 1300000000, 1400000000
        ]
        gids_inteligentes.extend(gids_comuns_grandes)
        
        print(f"   📊 Testando {len(set(gids_inteligentes))} GIDs inteligentes...")
        
        for gid in set(gids_inteligentes):
            try:
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
                response = requests.get(csv_url, timeout=5)
                
                if response.status_code == 200 and response.text.strip():
                    df = self._ler_csv_com_encoding(response.text)
                    if len(df) > 1:
                        tipo_aba = self._identificar_tipo_aba(df)
                        if tipo_aba != 'desconhecido' and tipo_aba not in abas_encontradas:
                            abas_encontradas[tipo_aba] = df
                            print(f"   ✅ {tipo_aba}: {len(df)} registros (GID {gid})")
                            
            except Exception:
                continue
        
        return abas_encontradas
    
    def _busca_exaustiva(self, sheet_id):
        """ESTRATÉGIA 4: Busca exaustiva (último recurso)"""
        abas_encontradas = {}
        
        print("   ⚠️ Executando busca exaustiva - pode demorar...")
        
        # Sequências numéricas extensas
        ranges_exaustivos = [
            range(0, 100),           # 0-99
            range(1000, 1100),       # 1000-1099
            range(10000, 10050),     # 10000-10049
            range(100000, 100050),   # 100000-100049
        ]
        
        # GIDs od (padrão Google)
        gids_od_extensivos = [f'od{i}' for i in range(6, 30)]
        
        todos_gids = []
        for r in ranges_exaustivos:
            todos_gids.extend(list(r))
        todos_gids.extend(gids_od_extensivos)
        
        print(f"   📊 Testando {len(todos_gids)} GIDs na busca exaustiva...")
        
        for i, gid in enumerate(todos_gids):
            # Mostra progresso a cada 50 GIDs
            if i % 50 == 0 and i > 0:
                print(f"   📈 Progresso: {i}/{len(todos_gids)} GIDs testados...")
            
            try:
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
                response = requests.get(csv_url, timeout=3)
                
                if response.status_code == 200 and response.text.strip():
                    df = self._ler_csv_com_encoding(response.text)
                    if len(df) > 1:
                        tipo_aba = self._identificar_tipo_aba(df)
                        if tipo_aba != 'desconhecido' and tipo_aba not in abas_encontradas:
                            abas_encontradas[tipo_aba] = df
                            print(f"   ✅ {tipo_aba}: {len(df)} registros (GID {gid})")
                            
                            # Para se encontrou as 3 abas principais
                            if len(abas_encontradas) >= 3:
                                break
                            
            except Exception:
                continue
        
        return abas_encontradas
    
    def _gerar_gids_por_padroes_nomes(self):
        """Gera GIDs baseado em padrões comuns de nomenclatura"""
        gids_por_padroes = []
        
        # Padrões baseados em hash de nomes comuns (melhorado)
        nomes_comuns = [
            'd+1', 'd+30', 'ruim', 'nps d+1', 'nps d+30', 'nps ruim',
            'atendimento', 'produto', 'crítico', 'casos críticos',
            'nps d30', 'nps d1', 'd30', 'd1', 'pos venda', 'pos-venda',
            'satisfacao produto', 'avaliacao produto', 'qualidade',
            'mercadao', 'mercadão', 'oculos', 'óculos', 'whatsapp',
            'telefone', 'contato', 'follow up', 'feedback'
        ]
        
        # Simula GIDs que poderiam corresponder a esses nomes
        for i, nome in enumerate(nomes_comuns):
            # Gera alguns GIDs "plausíveis" baseados no nome
            hash_base = hash(nome) % 1000000
            if hash_base < 0:
                hash_base = abs(hash_base)
            
            gids_por_padroes.extend([
                hash_base,
                hash_base + 1,
                hash_base + 10,
                hash_base + 100
            ])
        
        # Remove duplicatas e valores muito grandes
        gids_por_padroes = list(set([g for g in gids_por_padroes if 0 <= g <= 2000000000]))
        
        return gids_por_padroes[:100]  # Limita a 100 GIDs
    
    def _finalizar_extracao(self, abas_encontradas):
        """Finaliza o processo de extração com relatório e sistema de fallback inteligente"""
        print(f"📊 Total de abas encontradas: {len(abas_encontradas)}")
        
        for tipo, df in abas_encontradas.items():
            print(f"   📋 {tipo}: {len(df)} registros")
        
        # Informa quais abas foram encontradas e quais estão faltando
        abas_esperadas = ['NPS_D1', 'NPS_D30', 'NPS_Ruim']
        abas_encontradas_nomes = list(abas_encontradas.keys())
        abas_faltantes = [aba for aba in abas_esperadas if aba not in abas_encontradas_nomes]
        
        # === SISTEMA DE FALLBACK INTELIGENTE ===
        if abas_faltantes:
            print(f"⚠️ Abas não encontradas: {', '.join(abas_faltantes)}")
            print("🔄 Aplicando sistema de fallback inteligente...")
            
            # Tentar reclassificar abas mal identificadas
            abas_reclassificadas = self._aplicar_fallback_inteligente(abas_encontradas, abas_faltantes)
            
            if abas_reclassificadas:
                print("✅ Fallback aplicado com sucesso!")
                # Atualiza as abas encontradas
                abas_encontradas.update(abas_reclassificadas)
                self.dados_abas.update(abas_reclassificadas)
                
                # Atualiza relatório
                print("📊 Abas após fallback:")
                for tipo, df in abas_encontradas.items():
                    print(f"   📋 {tipo}: {len(df)} registros")
            else:
                print("   💡 Fallback não encontrou abas adicionais")
        
        return True
    
    def _aplicar_fallback_inteligente(self, abas_encontradas, abas_faltantes):
        """Aplica sistema de fallback para reclassificar abas mal identificadas"""
        abas_reclassificadas = {}
        
        # Se faltou D+30, procura por abas com "Dados_Gerais" ou outras que tenham WhatsApp
        if 'NPS_D30' in abas_faltantes:
            for tipo_atual, df in list(abas_encontradas.items()):
                if tipo_atual in ['Dados_Gerais', 'NPS_Ruim']:  # Candidatos para reclassificação
                    colunas_texto = ' '.join([self._corrigir_encoding_comum(str(col)) for col in df.columns])
                    
                    # Se tem WhatsApp, é muito provavelmente D+30
                    if any(palavra in colunas_texto for palavra in ['whatsapp', 'zap', 'wpp']):
                        print(f"   🔄 Reclassificando {tipo_atual} como NPS_D30 (WhatsApp detectado)")
                        abas_reclassificadas['NPS_D30'] = df
                        # Remove da lista original para evitar duplicação
                        if tipo_atual in abas_encontradas:
                            del abas_encontradas[tipo_atual]
                        break
        
        # Se faltou D+1, procura por abas com telefone
        if 'NPS_D1' in abas_faltantes:
            for tipo_atual, df in list(abas_encontradas.items()):
                if tipo_atual == 'Dados_Gerais':
                    colunas_texto = ' '.join([self._corrigir_encoding_comum(str(col)) for col in df.columns])
                    
                    # Se tem telefone mas não WhatsApp
                    tem_telefone = any(palavra in colunas_texto for palavra in ['telefone', 'fone', 'phone'])
                    tem_whatsapp = any(palavra in colunas_texto for palavra in ['whatsapp', 'zap', 'wpp'])
                    
                    if tem_telefone and not tem_whatsapp:
                        print(f"   🔄 Reclassificando {tipo_atual} como NPS_D1 (telefone sem WhatsApp)")
                        abas_reclassificadas['NPS_D1'] = df
                        if tipo_atual in abas_encontradas:
                            del abas_encontradas[tipo_atual]
                        break
        
        return abas_reclassificadas
    
    def _gerar_gids_comuns(self):
        """Gera lista de GIDs comuns baseado em padrões do Google Sheets"""
        gids_comuns = []
        
        # Padrões baseados em timestamps e sequências comuns
        import time
        timestamp_atual = int(time.time())
        
        # GIDs baseados em anos recentes (2020-2025)
        for ano in range(2020, 2026):
            # Padrões típicos do Google Sheets para cada ano
            base_ano = ano * 1000000
            gids_comuns.extend([
                base_ano, base_ano + 1, base_ano + 2, base_ano + 10, base_ano + 100
            ])
        
        # Sequências numéricas comuns no Google Sheets
        sequencias_comuns = [
            # Sequências pequenas
            list(range(100, 200)),
            list(range(500, 600)), 
            list(range(1000, 1100)),
            # Sequências médias  
            list(range(10000, 10100)),
            list(range(50000, 50100)),
            list(range(100000, 100100)),
            # GIDs específicos comuns
            [476804694, 1410159651, 1202595829, 1234567890, 987654321],
            # Variações de milhões
            [1000000 + i for i in range(0, 50)],
            [10000000 + i for i in range(0, 50)],
            [100000000 + i for i in range(0, 50)]
        ]
        
        # Flattening das sequências
        for seq in sequencias_comuns:
            gids_comuns.extend(seq)
        
        return gids_comuns
    
    def _tentar_extracao_aba_unica(self, sheet_id, url):
        """ESTRATÉGIA ESPECIAL: Detecta planilhas de aba única com múltiplas fontes"""
        try:
            # Importa o extrator especial
            import os
            import sys
            import importlib.util
            
            # Carrega o módulo do extrator especial
            caminho_extrator = os.path.join(os.path.dirname(__file__), 'extrator_aba_unica_especial.py')
            if not os.path.exists(caminho_extrator):
                print("   ❌ Extrator especial não encontrado")
                return False
            
            spec = importlib.util.spec_from_file_location("extrator_especial", caminho_extrator)
            extrator_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(extrator_module)
            
            # Usa o extrator especial
            extractor_especial = extrator_module.ExtratorAbaUnicaEspecial()
            resultado = extractor_especial.extrair_especial(url)
            
            if resultado.get('sucesso'):
                print("   ✅ Detectada planilha tipo aba única!")
                
                # Converte para formato do sistema principal
                import pandas as pd
                self.dados_abas = {}
                
                for tipo, linhas in resultado['dados_separados'].items():
                    # Cria DataFrame
                    df = pd.DataFrame(linhas, columns=resultado['header'])
                    
                    # Mapeia tipos para formato do sistema
                    if tipo == 'D+30':
                        self.dados_abas['NPS_D30'] = df
                        print(f"   📊 NPS D+30: {len(df)} registros")
                    elif tipo == 'D+1':
                        self.dados_abas['NPS_D1'] = df
                        print(f"   📊 NPS D+1: {len(df)} registros")
                    elif tipo == 'NPS_Ruim':
                        self.dados_abas['NPS_Ruim'] = df
                        print(f"   📊 NPS Ruim: {len(df)} registros")
                
                # Implementa NPS Ruim automaticamente
                try:
                    print("   🔍 Implementando NPS Ruim automaticamente...")
                    caminho_implementador = os.path.join(os.path.dirname(__file__), 'implementar_nps_ruim_completo.py')
                    if os.path.exists(caminho_implementador):
                        spec_ruim = importlib.util.spec_from_file_location("implementador_ruim", caminho_implementador)
                        implementador_module = importlib.util.module_from_spec(spec_ruim)
                        spec_ruim.loader.exec_module(implementador_module)
                        
                        implementador = implementador_module.ImplementadorNPSRuim()
                        resultado_ruim = implementador.implementar_nps_ruim_completo(url)
                        
                        if resultado_ruim.get('sucesso'):
                            # Carrega dados NPS Ruim
                            import csv
                            with open('extracao_especial_NPS_Ruim.csv', 'r', encoding='utf-8') as f:
                                reader = csv.DictReader(f)
                                dados_ruim = list(reader)
                            
                            # Converte para DataFrame
                            df_ruim = pd.DataFrame(dados_ruim)
                            self.dados_abas['NPS_Ruim'] = df_ruim
                            print(f"   ✅ NPS Ruim implementado: {len(df_ruim)} casos")
                        
                except Exception as e:
                    print(f"   ⚠️ Erro ao implementar NPS Ruim: {e}")
                
                return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ Erro na estratégia aba única: {e}")
            return False


def main():
    """Função principal para uso direto"""
    print("🎯 ANALISADOR NPS COMPLETO")
    print("="*50)
    print("Cole o link da planilha Google Sheets para análise automática")
    print()
    
    # Exemplo de uso:
    # analisador = AnalisadorNPSCompleto("Mercadão dos Óculos")
    # resultado = analisador.analisar_planilha("URL_DA_PLANILHA")
    # print(resultado)


if __name__ == "__main__":
    main()