#!/usr/bin/env python3
"""
Adaptador de Dados - Converte dados do novo sistema para formato antigo
Autor: Claude Code  
Data: 27/07/2025
"""

import pandas as pd
from datetime import datetime, timedelta


class AdaptadorDados:
    """Adapta dados do novo sistema para compatibilidade com IA existente"""
    
    def __init__(self):
        pass
    
    def converter_para_formato_antigo(self, dados_novos, data_inicio=None, data_fim=None):
        """
        Converte dados do analisador_nps_completo para formato esperado pelo analisador_ia_simple
        
        Input: dados do AnalisadorNPSCompleto.dados_abas
        Output: formato compatível com AnalisadorIACustomizado
        
        Args:
            dados_novos: dados das abas extraídas
            data_inicio: data de início do filtro (formato YYYY-MM-DD ou datetime)
            data_fim: data de fim do filtro (formato YYYY-MM-DD ou datetime)
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
                    
                    # Aplica filtro por data se especificado
                    if data_inicio or data_fim:
                        df_convertido = self._filtrar_por_data(df_convertido, data_inicio, data_fim)
                        
                        # Se após filtro não há dados, pula esta aba
                        if df_convertido is None or len(df_convertido) == 0:
                            print(f"   ⚠️ {tipo_aba}: Nenhum registro encontrado no período especificado")
                            continue
                        else:
                            print(f"   ✅ {tipo_aba}: {len(df_convertido)} registros após filtro por data")
                    
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
    
    def _filtrar_por_data(self, df, data_inicio=None, data_fim=None):
        """Filtra DataFrame por período de datas"""
        try:
            # Procura colunas de data possíveis
            colunas_data = self._encontrar_colunas_data(df)
            
            if not colunas_data:
                print("   ⚠️ Nenhuma coluna de data encontrada - retornando dados sem filtro")
                return df
            
            # Usa a primeira coluna de data encontrada
            coluna_data = colunas_data[0]
            print(f"   📅 Usando coluna de data: '{coluna_data}'")
            
            # Converte strings para datetime se necessário
            if data_inicio and isinstance(data_inicio, str):
                data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            if data_fim and isinstance(data_fim, str):
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
            
            # Converte coluna de data para datetime
            df_filtrado = df.copy()
            df_filtrado[coluna_data] = pd.to_datetime(df_filtrado[coluna_data], errors='coerce')
            
            # Remove linhas com datas inválidas
            df_filtrado = df_filtrado.dropna(subset=[coluna_data])
            
            # Aplica filtros
            if data_inicio:
                df_filtrado = df_filtrado[df_filtrado[coluna_data] >= data_inicio]
                print(f"   📅 Filtro aplicado: data >= {data_inicio.strftime('%d/%m/%Y')}")
            
            if data_fim:
                # Adiciona 23:59:59 ao fim do dia para incluir todo o dia final
                data_fim_completa = data_fim + timedelta(hours=23, minutes=59, seconds=59)
                df_filtrado = df_filtrado[df_filtrado[coluna_data] <= data_fim_completa]
                print(f"   📅 Filtro aplicado: data <= {data_fim.strftime('%d/%m/%Y')}")
            
            print(f"   📊 Registros antes do filtro: {len(df)}")
            print(f"   📊 Registros após filtro: {len(df_filtrado)}")
            
            return df_filtrado
            
        except Exception as e:
            print(f"   ⚠️ Erro no filtro por data: {str(e)} - retornando dados sem filtro")
            return df
    
    def _encontrar_colunas_data(self, df):
        """Encontra colunas que podem conter datas"""
        colunas_data = []
        
        # Padrões comuns para colunas de data
        padroes_data = [
            'data', 'date', 'timestamp', 'time', 'created', 'modified',
            'data_criacao', 'data_modificacao', 'data_resposta', 'data_avaliacao',
            'created_at', 'updated_at', 'datetime', 'dt'
        ]
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            
            # Verifica se o nome da coluna contém padrões de data
            for padrao in padroes_data:
                if padrao in col_lower:
                    colunas_data.append(col)
                    break
            
            # Verifica se o conteúdo parece data (amostra das primeiras linhas)
            if col not in colunas_data and len(df) > 0:
                try:
                    amostra = df[col].dropna().head(3)
                    if len(amostra) > 0:
                        # Tenta converter para datetime
                        pd.to_datetime(amostra, errors='raise')
                        colunas_data.append(col)
                        print(f"   🔍 Coluna '{col}' detectada como data pelo conteúdo")
                except:
                    continue
        
        return colunas_data


if __name__ == "__main__":
    print("🔄 Adaptador de Dados pronto!")
    # Teste básico
    adaptador = AdaptadorDados()
    print("✅ Inicialização concluída!")
    
    # Teste do filtro por data
    print("\n🧪 Testando filtro por data...")
    import pandas as pd
    
    # Cria DataFrame de teste
    dados_teste = {
        'Data': ['2025-01-15', '2025-01-20', '2025-01-25', '2025-02-01'],
        'Nome': ['João', 'Maria', 'Pedro', 'Ana'],
        'Avaliacao': [8, 9, 6, 10]
    }
    df_teste = pd.DataFrame(dados_teste)
    
    # Testa filtro
    df_filtrado = adaptador._filtrar_por_data(df_teste, '2025-01-18', '2025-01-31')
    print(f"Resultado: {len(df_filtrado)} registros filtrados")
    print("✅ Teste concluído!")