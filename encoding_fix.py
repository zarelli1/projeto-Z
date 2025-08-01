#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correção de encoding para Windows - Sistema NPS
"""

import sys
import os
import re

def setup_windows_encoding():
    """Configura encoding UTF-8 no Windows"""
    if os.name == 'nt':  # Windows
        try:
            # Configura console para UTF-8
            os.system('chcp 65001 > nul 2>&1')
            
            # Redefine stdout/stderr para UTF-8 com fallback
            import codecs
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
            if hasattr(sys.stderr, 'buffer'):
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')
                
        except Exception:
            pass  # Ignora erros de configuração

def safe_print(text):
    """Print seguro que funciona no Windows com emojis"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        # Remove emojis e caracteres problemáticos
        clean_text = re.sub(r'[^\x00-\x7F\u00C0-\u017F]+', '?', str(text))
        print(clean_text)
    except Exception:
        # Último recurso
        print(str(text).encode('ascii', errors='replace').decode('ascii'))

def safe_emoji_replace(text):
    """Substitui emojis por texto equivalente"""
    emoji_map = {
        '💾': '[CACHE]',
        '⚠️': '[AVISO]', 
        '✅': '[OK]',
        '❌': '[ERRO]',
        '🔍': '[BUSCA]',
        '📊': '[DADOS]',
        '🚀': '[INICIO]',
        '🎉': '[SUCESSO]',
        '🟢': '[PROMOTORES]',
        '🟡': '[NEUTROS]', 
        '🔴': '[DETRATORES]',
        '⭐': '[ESTRELA]'
    }
    
    result = str(text)
    for emoji, replacement in emoji_map.items():
        result = result.replace(emoji, replacement)
    
    return result

# Configura encoding automaticamente ao importar
setup_windows_encoding()

# Substitui print global por versão segura
import builtins
original_print = builtins.print

def windows_safe_print(*args, **kwargs):
    """Print replacement que é seguro no Windows"""
    try:
        original_print(*args, **kwargs)
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Converte argumentos para formato seguro
        safe_args = []
        for arg in args:
            safe_args.append(safe_emoji_replace(arg))
        original_print(*safe_args, **kwargs)
    except Exception:
        # Último recurso - imprime versão ASCII
        ascii_args = []
        for arg in args:
            ascii_args.append(str(arg).encode('ascii', errors='replace').decode('ascii'))
        original_print(*ascii_args, **kwargs)

# Substitui print globalmente apenas no Windows
if os.name == 'nt':
    builtins.print = windows_safe_print