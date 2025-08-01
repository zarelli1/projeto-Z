#!/usr/bin/env python3
"""
Verifica configuração da API key
"""

import os
from dotenv import load_dotenv

def check_api_key():
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    print("VERIFICACAO OPENAI_API_KEY")
    print("=" * 30)
    
    if not api_key:
        print("❌ OPENAI_API_KEY não configurada")
        return False
    elif api_key == 'your_openai_api_key_here':
        print("⚠️  OPENAI_API_KEY é placeholder - precisa da chave real")
        return False
    elif api_key.startswith('sk-'):
        print("✅ OPENAI_API_KEY configurada corretamente")
        print(f"   Prefixo: {api_key[:15]}...")
        return True
    else:
        print("⚠️  OPENAI_API_KEY configurada mas formato incorreto")
        print(f"   Valor atual: {api_key[:20]}...")
        return False

def show_instructions():
    print("\nINSTRUCOES PARA CONFIGURAR:")
    print("1. Obtenha sua chave em: https://platform.openai.com/api-keys")
    print("2. Edite o arquivo .env")
    print("3. Substitua 'your_openai_api_key_here' pela chave real")
    print("4. A chave deve começar com 'sk-'")
    print("\nExemplo no .env:")
    print("OPENAI_API_KEY=sk-proj-abcdef123456...")

if __name__ == "__main__":
    if not check_api_key():
        show_instructions()
    else:
        print("\n✅ Sistema pronto para usar IA!")