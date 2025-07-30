#!/usr/bin/env python3
"""
Sistema NPS Customizado - Para extrair e analisar abas D+1, D+30 e NPS Ruim
Autor: Claude Code
Data: 26/07/2025
"""

import sys
import os
from datetime import datetime
from analisador_nps_completo import AnalisadorNPSCompleto
from analisador_ia_simple import AnalisadorIACustomizado
from gerador_pdf import GeradorPDFCustomizado
from adaptador_dados import AdaptadorDados


def exibir_menu_customizado():
    """Exibe o menu do sistema customizado"""
    print("\n🎯 SISTEMA ANÁLISE MERCADÃO DOS ÓCULOS")
    print("=" * 65)
    print("📊 Especializado em D+1 (Atendimento) | D+30 (Produto) | NPS Ruim")
    print("=" * 65)
    print("1. 📋 Gerar Relatório Completo de Pós-venda")
    print("2. 🔍 Testar Extração de Abas Específicas")
    print("3. 📄 Instruções de Configuração")
    print("4. 🔧 Configurar Autenticação")
    print("5. 🚪 Sair")
    print("=" * 65)


def mostrar_instrucoes_customizadas():
    """Mostra instruções específicas para as abas"""
    print("\n📋 INSTRUÇÕES PARA ABAS ESPECÍFICAS")
    print("=" * 60)
    print("🎯 ABAS NECESSÁRIAS na planilha:")
    print()
    print("1. 📊 ABA 'NPS D+1' (Avaliação de Atendimento):")
    print("   Colunas: ID, Data, Nome Completo, Primeiro Nome,")
    print("   Telefone, Avaliação, Comentário, Vendedor, Loja, Abandono")
    print()
    print("2. 🛍️ ABA 'NPS D+30' (Avaliação de Produto):")
    print("   Colunas: Id Bot, Data, Nome Completo, Primeiro Nome,")
    print("   WhatsApp, Avaliação, Comentário, Vendedor, Loja, Abandono")
    print()
    print("3. ⚠️ ABA 'NPS Ruim' (Casos Críticos):")
    print("   Colunas: Id Bot, Fonte, Data, Nome Completo, Primeiro Nome,")
    print("   Telefone, Avaliação, Comentário, Vendedor, Loja, Situação,")
    print("   Comentário da Resolução, Data Resolução")
    print()
    print("💡 CONFIGURAÇÃO da planilha:")
    print("   - Deixe a planilha PÚBLICA no Google Sheets")
    print("   - OU configure autenticação (opção 4)")
    print("   - Certifique-se que as abas tenham os nomes EXATOS:")
    print("     'NPS D+1', 'NPS D+30', 'NPS Ruim'")
    print("   - Nomes aceitos (case insensitive):")
    print("     • NPS D+1, NPS d+1, nps d+1")
    print("     • NPS D+30, NPS d+30, nps d+30") 
    print("     • NPS Ruim, NPS ruim, nps ruim")
    print()
    input("Pressione Enter para voltar ao menu...")


def processar_relatorio_customizado():
    """Processa geração de relatório customizado"""
    print("\n📊 GERAÇÃO DE RELATÓRIO MERCADÃO DOS ÓCULOS")
    print("=" * 65)
    
    try:
        # 1. Coleta informações
        print("\n📋 CONFIGURAÇÃO DO RELATÓRIO")
        print("-" * 40)
        
        nome_loja = input("Nome da unidade (ex: MDO Colombo): ").strip()
        if not nome_loja:
            nome_loja = "MDO"
        
        url = input("URL do Google Sheets: ").strip()
        if not url:
            print("❌ URL não fornecida!")
            return False
        
        # 2. EXTRAIR DADOS COM NOVO SISTEMA INTELIGENTE
        print(f"\n🎯 PASSO 1: Extraindo dados com IA de '{nome_loja}'...")
        print("🔍 Buscando abas automaticamente: D+1, D+30, NPS Ruim...")
        
        # Usa o novo analisador completo
        analisador_completo = AnalisadorNPSCompleto(nome_loja)
        
        # Extração automática das abas
        if not analisador_completo._extrair_abas_automaticamente(url):
            print("❌ Falha na conexão com a planilha!")
            print("💡 Verifique se:")
            print("   - A planilha está pública (compartilhamento aberto)")
            print("   - A URL está correta")
            print("   - Ou configure autenticação (opção 4 do menu)")
            return False
        
        # Padroniza dados
        analisador_completo._padronizar_todos_dados()
        
        if not analisador_completo.dados_abas:
            print("❌ Nenhum dado válido encontrado nas abas!")
            print("💡 Verifique se sua planilha tem as abas:")
            print("   - D+1 (dados de atendimento)")
            print("   - D+30 (dados de produto)")  
            print("   - NPS Ruim (casos críticos)")
            return False
        
        # Converte dados para formato compatível
        adaptador = AdaptadorDados()
        dados_segmentados = adaptador.converter_para_formato_antigo(analisador_completo.dados_abas)
        
        if not dados_segmentados or dados_segmentados.get('todos') is None or (hasattr(dados_segmentados.get('todos'), 'empty') and dados_segmentados['todos'].empty) or len(dados_segmentados.get('todos', [])) == 0:
            print("❌ Erro na conversão dos dados!")
            return False
        
        # Mostra resumo da extração
        print(f"\n✅ DADOS EXTRAÍDOS COM SUCESSO:")
        total_registros = len(dados_segmentados['todos'])
        print(f"📊 Total de registros: {total_registros}")
        
        for tipo in ['atendimento', 'produto', 'nps_ruim']:
            if dados_segmentados.get(tipo) is not None:
                count = len(dados_segmentados[tipo])
                tipo_nome = {
                    'atendimento': 'D+1 (Atendimento)',
                    'produto': 'D+30 (Produto)', 
                    'nps_ruim': 'NPS Ruim'
                }[tipo]
                print(f"   • {tipo_nome}: {count} registros")
            else:
                tipo_nome = {
                    'atendimento': 'D+1 (Atendimento)',
                    'produto': 'D+30 (Produto)',
                    'nps_ruim': 'NPS Ruim'
                }[tipo]
                print(f"   ⚠️ {tipo_nome}: Não encontrado")
        
        # Mostra amostra dos dados
        print(f"\n📋 AMOSTRA DOS DADOS:")
        todos_df = dados_segmentados.get('todos')
        if todos_df is not None and not todos_df.empty:
            colunas_principais = [col for col in todos_df.columns 
                                if col in ['Data', 'Nome Completo', 'Vendedor', 'Loja', 'Avaliação', 'Tipo_Aba']]
            if colunas_principais:
                print(todos_df[colunas_principais].head(3).to_string())
        
        # 3. ANÁLISE CUSTOMIZADA COM IA
        print(f"\n🤖 PASSO 2: Análise inteligente especializada...")
        print("🧠 Processando dados com foco em Mercadão dos Óculos...")
        
        try:
            # Cria analisador customizado
            analisador_ia = AnalisadorIACustomizado(dados_segmentados, nome_loja)
            relatorio_ia = analisador_ia.gerar_analise_completa()
            
            if relatorio_ia:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Salva versão TXT
                nome_arquivo_txt = f"relatorio_pos_venda_{nome_loja.replace(' ', '_')}_{timestamp}.txt"
                with open(nome_arquivo_txt, 'w', encoding='utf-8') as f:
                    f.write(relatorio_ia)
                print(f"✅ Relatório TXT salvo: {nome_arquivo_txt}")
                
                # 4. GERA PDF CUSTOMIZADO
                print(f"\n📄 PASSO 3: Gerando PDF estilo Mercadão dos Óculos...")
                
                gerador_pdf = GeradorPDFCustomizado()
                nome_arquivo_pdf = f"relatorio_pos_venda_{nome_loja.replace(' ', '_')}_{timestamp}.pdf"
                pdf_gerado = gerador_pdf.gerar_pdf_customizado(relatorio_ia, nome_loja, nome_arquivo_pdf)
                
                if pdf_gerado:
                    print(f"✅ PDF customizado gerado: {pdf_gerado}")
                else:
                    print("⚠️ Erro ao gerar PDF, mas relatório TXT disponível")
                
                # 5. EXIBE PRÉVIA E RESUMO
                print(f"\n📄 PRÉVIA DO RELATÓRIO:")
                print("="*65)
                # Mostra primeiras linhas do relatório
                linhas_preview = relatorio_ia.split('\n')[:15]
                for linha in linhas_preview:
                    if linha.strip():
                        print(linha)
                if len(relatorio_ia.split('\n')) > 15:
                    print("...")
                print("="*65)
                
                # Resumo final
                print(f"\n🎉 RELATÓRIO CONCLUÍDO - {nome_loja}")
                print(f"📊 {total_registros} registros analisados")
                
                # Mostra distribuição por aba
                todos_df = dados_segmentados.get('todos')
                if todos_df is not None and not todos_df.empty and 'Tipo_Aba' in todos_df.columns:
                    resumo_tipos = todos_df['Tipo_Aba'].value_counts()
                    print(f"📋 Distribuição:")
                    for tipo, count in resumo_tipos.items():
                        tipo_nome = {
                            'atendimento': 'Atendimento (D+1)',
                            'produto': 'Produto (D+30)',
                            'nps_ruim': 'NPS Ruim'
                        }.get(tipo, tipo)
                        print(f"   • {tipo_nome}: {count}")
                
                print(f"✅ Análise especializada Mercadão dos Óculos completa!")
                
            else:
                print("⚠️ Erro na geração da análise IA")
                
        except Exception as e:
            print(f"⚠️ Erro na análise IA: {str(e)}")
            print("💡 Verifique a configuração da API OpenAI")
        
        return True
            
    except KeyboardInterrupt:
        print("\n\n👋 Operação cancelada pelo usuário")
        return False
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        return False


def testar_extracao_abas():
    """Testa extração das abas específicas"""
    print("\n🔍 TESTE DE EXTRAÇÃO DAS ABAS ESPECÍFICAS")
    print("=" * 60)
    
    url = input("URL da planilha para teste: ").strip()
    
    if not url:
        print("❌ URL não fornecida!")
        return
    
    try:
        print("🔍 Testando extração...")
        extractor = NPSExtractorCustomizado()
        
        if extractor.conectar_sheets(url):
            dados = extractor.extrair_dados_segmentados()
            
            if dados and dados.get('todos') is not None and len(dados.get('todos', [])) > 0:
                print(f"\n✅ TESTE CONCLUÍDO:")
                
                for tipo, df in dados.items():
                    if df is not None and tipo != 'todos' and len(df) > 0:
                        print(f"\n📊 {tipo.upper()}:")
                        print(f"   • Registros: {len(df)}")
                        print(f"   • Colunas: {list(df.columns)}")
                        
                        # Mostra amostra
                        if len(df) > 0:
                            print("   • Amostra:")
                            print(df.head(2).to_string())
                
                print(f"\n🎯 RESUMO GERAL:")
                print(f"   • Total combinado: {len(dados['todos'])} registros")
                print(f"   • Abas encontradas: {dados['todos']['Aba_Origem'].nunique()} abas")
                
            else:
                print("❌ Nenhum dado extraído")
        else:
            print("❌ Falha na conexão")
            
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
    
    input("\nPressione Enter para voltar ao menu...")


def configurar_autenticacao_customizada():
    """Menu de configuração simplificado"""
    print("\n🔐 CONFIGURAÇÃO DE AUTENTICAÇÃO")
    print("=" * 50)
    print("💡 Para acessar planilhas privadas, configure:")
    print()
    print("1. 🔑 OAuth2 (Recomendado)")
    print("2. 🔐 Service Account")  
    print("3. 📊 Verificar Status")
    print("4. 🔙 Voltar")
    print()
    
    opcao = input("Escolha uma opção (1-4): ").strip()
    
    if opcao == '1':
        print("\n🔑 CONFIGURAÇÃO OAUTH2:")
        print("Execute: python oauth2_working.py")
        print("Siga as instruções para autorizar o acesso")
    elif opcao == '2':
        print("\n🔐 CONFIGURAÇÃO SERVICE ACCOUNT:")
        print("1. Vá ao Google Cloud Console")
        print("2. Crie um Service Account")
        print("3. Baixe o arquivo JSON")
        print("4. Salve como: credentials/service-account.json")
    elif opcao == '3':
        # Verifica status
        print("\n📊 STATUS DA AUTENTICAÇÃO:")
        if os.path.exists('credentials/oauth2_token_working.json'):
            print("✅ OAuth2: Configurado")
        else:
            print("❌ OAuth2: Não configurado")
            
        if os.path.exists('credentials/service-account.json'):
            print("✅ Service Account: Configurado")
        else:
            print("❌ Service Account: Não configurado")
            
        print("🌐 Método Público: Sempre disponível")
    
    input("\nPressione Enter para continuar...")


def main():
    """Interface principal do sistema customizado"""
    print("🎯 SISTEMA ANÁLISE MERCADÃO DOS ÓCULOS")
    print("Especializado em D+1, D+30 e NPS Ruim")
    print("Autor: Claude Code | Data: 2025")
    
    while True:
        try:
            exibir_menu_customizado()
            
            opcao = input("\nEscolha uma opção (1-5): ").strip()
            
            if opcao == '1':
                processar_relatorio_customizado()
                input("\nPressione Enter para voltar ao menu...")
            elif opcao == '2':
                testar_extracao_abas()
            elif opcao == '3':
                mostrar_instrucoes_customizadas()
            elif opcao == '4':
                configurar_autenticacao_customizada()
            elif opcao == '5':
                print("\n👋 Saindo do sistema...")
                break
            else:
                print("❌ Opção inválida! Escolha 1, 2, 3, 4 ou 5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Saindo do sistema...")
            break
        except Exception as e:
            print(f"\n❌ Erro inesperado: {str(e)}")
            try:
                input("Pressione Enter para continuar...")
            except EOFError:
                print("\n👋 Saindo do sistema...")
                break


if __name__ == "__main__":
    main()