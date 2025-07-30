#!/usr/bin/env python3
"""
Adaptador de Dados - Converte dados do novo sistema para formato antigo
Autor: Claude Code  
Data: 27/07/2025
"""

import pandas as pd


class AdaptadorDados:
    """Adapta dados do novo sistema para compatibilidade com IA existente"""
    
    def __init__(self):
        pass
    
    def converter_para_formato_antigo(self, dados_novos):
        """
        Converte dados do analisador_nps_completo para formato esperado pelo analisador_ia_simple
        
        Input: dados do AnalisadorNPSCompleto.dados_abas
        Output: formato compatível com AnalisadorIACustomizado
        """
        try:
            if not dados_novos:
                return None
            
            dados_convertidos = {
                'atendimento': None,
                'produto': None,
                'nps_ruim': None,
                'todos': None
            }
            
            todos_dados = []
            
            # Converte cada aba
            for tipo_aba, df in dados_novos.items():
                if df is not None and len(df) > 0:
                    # Padroniza nomes das colunas para formato antigo
                    df_convertido = self._padronizar_colunas_antigas(df.copy())
                    
                    # Adiciona tipo da aba
                    if tipo_aba == 'NPS_D1':
                        df_convertido['Tipo_Aba'] = 'atendimento'
                        dados_convertidos['atendimento'] = df_convertido
                    elif tipo_aba == 'NPS_D30':
                        df_convertido['Tipo_Aba'] = 'produto'
                        dados_convertidos['produto'] = df_convertido
                    elif tipo_aba == 'NPS_Ruim':
                        df_convertido['Tipo_Aba'] = 'nps_ruim'
                        dados_convertidos['nps_ruim'] = df_convertido
                    
                    todos_dados.append(df_convertido)
            
            # Combina todos os dados
            if todos_dados:
                dados_convertidos['todos'] = pd.concat(todos_dados, ignore_index=True)
            
            return dados_convertidos
            
        except Exception as e:
            print(f"⚠️ Erro na conversão de dados: {str(e)}")
            return None
    
    def _padronizar_colunas_antigas(self, df):
        """Padroniza nomes das colunas para formato esperado pelo sistema antigo"""
        try:
            # Mapeamento de colunas novas para antigas
            mapeamento_colunas = {
                # Nomes comuns
                'id': 'ID',
                'id_bot': 'ID Bot',
                'data': 'Data',
                'nome_completo': 'Nome Completo',
                'primeiro_nome': 'Primeiro Nome',
                'telefone': 'Telefone',
                'whatsapp': 'WhatsApp',
                'avaliaacaao': 'Avaliação',
                'avaliacao': 'Avaliação',
                'comentaario': 'Comentário',
                'comentario': 'Comentário',
                'vendedor': 'Vendedor',
                'loja': 'Loja',
                'abandono': 'Abandono',
                'situaacaao': 'Situação',
                'situacao': 'Situação',
                'comentaario_da_resoluacaao': 'Comentário da Resolução',
                'comentario_da_resolucao': 'Comentário da Resolução',
                'data_resouacaao': 'Data Resolução',
                'data_resolucao': 'Data Resolução',
                'fonte': 'Fonte'
            }
            
            # Renomeia colunas
            colunas_renomeadas = {}
            for col in df.columns:
                col_lower = str(col).lower().strip()
                if col_lower in mapeamento_colunas:
                    colunas_renomeadas[col] = mapeamento_colunas[col_lower]
                else:
                    # Mantém nome original se não encontrar mapeamento
                    colunas_renomeadas[col] = col
            
            df = df.rename(columns=colunas_renomeadas)
            
            # Garante que Avaliação seja numérica
            if 'Avaliação' in df.columns:
                df['Avaliação'] = pd.to_numeric(df['Avaliação'], errors='coerce')
            
            return df
            
        except Exception as e:
            print(f"⚠️ Erro na padronização de colunas: {str(e)}")
            return df


if __name__ == "__main__":
    print("🔄 Adaptador de Dados pronto!")
    # Teste básico
    adaptador = AdaptadorDados()
    print("✅ Inicialização concluída!")