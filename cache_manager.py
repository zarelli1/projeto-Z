#!/usr/bin/env python3
"""
Cache Manager - Sistema de cache para otimizar performance
Autor: Claude Code
Data: 01/08/2025
"""

import os
import json
import hashlib
import time
from datetime import datetime, timedelta
import pickle

class CacheManager:
    """Gerenciador de cache inteligente para otimizar análises recorrentes"""
    
    def __init__(self, cache_dir="cache", ttl_hours=1):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_hours * 3600  # TTL de 1 hora como especificado
        self.url_cache = {}  # URLs testadas
        self.analysis_cache = {}  # Resultados análise  
        self.cache_times = {}  # Timestamps
        
        # Cria diretório de cache se não existir
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Limpa cache expirado na inicialização
        self._cleanup_expired_cache()
    
    def should_refresh(self, key):
        """Verifica se o cache deve ser atualizado"""
        if key not in self.cache_times:
            return True
        return time.time() - self.cache_times[key] > self.ttl_seconds
    
    def _get_cache_key(self, sheets_url, filters=None):
        """Gera chave única para cache baseada na URL e filtros"""
        cache_data = {
            'url': sheets_url,
            'filters': filters or {}
        }
        
        # Gera hash MD5 para chave única
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key):
        """Retorna caminho completo do arquivo de cache"""
        return os.path.join(self.cache_dir, f"{cache_key}.cache")
    
    def _is_cache_valid(self, cache_path):
        """Verifica se o cache ainda está válido (não expirou)"""
        if not os.path.exists(cache_path):
            return False
        
        # Verifica idade do arquivo
        cache_time = os.path.getmtime(cache_path)
        current_time = time.time()
        
        return (current_time - cache_time) < self.ttl_seconds
    
    def get_cached_data(self, sheets_url, filters=None):
        """Recupera dados do cache se disponível e válido"""
        cache_key = self._get_cache_key(sheets_url, filters)
        cache_path = self._get_cache_path(cache_key)
        
        if not self._is_cache_valid(cache_path):
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            
            print(f"💾 Cache encontrado para URL (idade: {self._get_cache_age(cache_path)})")
            return cached_data
            
        except Exception as e:
            print(f"⚠️ Erro ao ler cache: {e}")
            # Remove cache corrompido
            try:
                os.remove(cache_path)
            except:
                pass
            return None
    
    def save_to_cache(self, sheets_url, data, filters=None):
        """Salva dados no cache"""
        try:
            cache_key = self._get_cache_key(sheets_url, filters)
            cache_path = self._get_cache_path(cache_key)
            
            # Dados para cache incluem timestamp
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            print(f"💾 Dados salvos no cache")
            
        except Exception as e:
            print(f"⚠️ Erro ao salvar cache: {e}")
    
    def _get_cache_age(self, cache_path):
        """Retorna idade do cache em formato legível"""
        cache_time = os.path.getmtime(cache_path)
        age_seconds = time.time() - cache_time
        
        if age_seconds < 60:
            return f"{int(age_seconds)}s"
        elif age_seconds < 3600:
            return f"{int(age_seconds/60)}min"
        else:
            return f"{int(age_seconds/3600)}h"
    
    def _cleanup_expired_cache(self):
        """Remove arquivos de cache expirados"""
        if not os.path.exists(self.cache_dir):
            return
        
        cleaned_count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.cache'):
                cache_path = os.path.join(self.cache_dir, filename)
                if not self._is_cache_valid(cache_path):
                    try:
                        os.remove(cache_path)
                        cleaned_count += 1
                    except:
                        pass
        
        if cleaned_count > 0:
            print(f"[CACHE] {cleaned_count} arquivos de cache expirados removidos")
    
    def clear_all_cache(self):
        """Remove todo o cache"""
        if not os.path.exists(self.cache_dir):
            return
        
        cleared_count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.cache'):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                    cleared_count += 1
                except:
                    pass
        
        print(f"[CACHE] {cleared_count} arquivos de cache removidos")
    
    def get_cache_stats(self):
        """Retorna estatísticas do cache"""
        if not os.path.exists(self.cache_dir):
            return {'total_files': 0, 'valid_files': 0, 'expired_files': 0, 'total_size_mb': 0}
        
        total_files = 0
        valid_files = 0
        expired_files = 0
        total_size = 0
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.cache'):
                cache_path = os.path.join(self.cache_dir, filename)
                total_files += 1
                total_size += os.path.getsize(cache_path)
                
                if self._is_cache_valid(cache_path):
                    valid_files += 1
                else:
                    expired_files += 1
        
        return {
            'total_files': total_files,
            'valid_files': valid_files,
            'expired_files': expired_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }


# Instância global do cache manager
cache_manager = CacheManager()

if __name__ == "__main__":
    print("Cache Manager - Sistema de Cache Inteligente")
    print("=" * 50)
    
    # Exibe estatísticas
    stats = cache_manager.get_cache_stats()
    print(f"Estatisticas do Cache:")
    print(f"   Total de arquivos: {stats['total_files']}")
    print(f"   Arquivos validos: {stats['valid_files']}")
    print(f"   Arquivos expirados: {stats['expired_files']}")
    print(f"   Tamanho total: {stats['total_size_mb']} MB")
    
    print("\nCache Manager inicializado!")