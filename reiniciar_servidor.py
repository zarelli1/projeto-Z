#!/usr/bin/env python3
"""
Script para reiniciar o servidor Flask
"""

import subprocess
import sys
import time
import os
import signal

def find_and_kill_server():
    """Encontra e mata processos do servidor Flask"""
    try:
        # Para Windows, usar tasklist e taskkill
        if sys.platform.startswith('win'):
            # Encontra processos Python rodando server.py
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Skip header
                    if 'server.py' in line or 'python.exe' in line:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            pid = parts[1].strip('"')
                            try:
                                subprocess.run(['taskkill', '/PID', pid, '/F'], 
                                             capture_output=True)
                                print(f"Processo {pid} encerrado")
                            except:
                                pass
        
    except Exception as e:
        print(f"Erro ao encerrar processos: {e}")

def start_server():
    """Inicia o servidor Flask"""
    try:
        os.chdir('frontend')
        print("Iniciando servidor Flask...")
        print("Acesse: http://localhost:3000")
        print("Pressione Ctrl+C para parar")
        
        # Inicia o servidor
        subprocess.run([sys.executable, 'server.py'])
        
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")

def main():
    print("REINICIANDO SERVIDOR NPS")
    print("=" * 30)
    
    # Para processos existentes
    print("1. Encerrando processos existentes...")
    find_and_kill_server()
    time.sleep(2)
    
    # Inicia novo servidor
    print("2. Iniciando novo servidor...")
    start_server()

if __name__ == "__main__":
    main()