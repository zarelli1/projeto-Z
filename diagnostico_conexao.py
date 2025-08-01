#!/usr/bin/env python3
"""
Diagnóstico completo de conexão do sistema NPS
"""

import requests
import json
import time

def test_all_endpoints():
    base_url = "http://localhost:3000"
    
    print("DIAGNOSTICO COMPLETO DE CONEXAO")
    print("=" * 50)
    print(f"URL Base: {base_url}")
    print()
    
    endpoints = [
        ("/", "GET", None, "Interface principal"),
        ("/api/health", "GET", None, "Health check"),
        ("/styles.css", "GET", None, "Arquivo CSS"),
        ("/nps-analyzer.js", "GET", None, "Arquivo JavaScript"),
        ("/api/test", "POST", {"sheets_url": "https://docs.google.com/spreadsheets/d/invalid"}, "Teste de API")
    ]
    
    results = []
    
    for endpoint, method, data, description in endpoints:
        print(f"Testando: {description}")
        print(f"  {method} {endpoint}")
        
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=15)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                if endpoint == "/api/health":
                    try:
                        json_data = response.json()
                        print(f"  Dados: {json_data}")
                    except:
                        print("  Resposta nao e JSON")
                elif endpoint == "/api/test":
                    try:
                        json_data = response.json()
                        print(f"  Success: {json_data.get('success')}")
                        if not json_data.get('success'):
                            print(f"  Erro: {json_data.get('error', 'N/A')}")
                    except:
                        print("  Resposta nao e JSON")
                else:
                    print(f"  Tamanho: {len(response.text)} chars")
                
                results.append((description, "OK"))
            else:
                print(f"  ERRO: {response.status_code}")
                results.append((description, f"ERRO {response.status_code}"))
                
        except requests.exceptions.ConnectionError:
            print("  ERRO: Conexao recusada - servidor nao esta rodando")
            results.append((description, "SEM CONEXAO"))
        except requests.exceptions.Timeout:
            print("  ERRO: Timeout - servidor demorou muito")
            results.append((description, "TIMEOUT"))
        except Exception as e:
            print(f"  ERRO: {e}")
            results.append((description, f"ERRO: {e}"))
        
        print()
    
    # Resumo
    print("RESUMO DOS TESTES:")
    print("-" * 30)
    ok_count = 0
    for desc, status in results:
        status_icon = "✓" if status == "OK" else "✗"
        print(f"{status_icon} {desc}: {status}")
        if status == "OK":
            ok_count += 1
    
    print()
    print(f"RESULTADO: {ok_count}/{len(results)} testes passaram")
    
    if ok_count == len(results):
        print("\n🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print("Acesse: http://localhost:3000")
    elif ok_count == 0:
        print("\n❌ SERVIDOR NAO ESTA RODANDO")
        print("Execute: cd frontend && python server.py")
    else:
        print(f"\n⚠️ ALGUNS PROBLEMAS ENCONTRADOS ({len(results)-ok_count} falhas)")

if __name__ == "__main__":
    test_all_endpoints()