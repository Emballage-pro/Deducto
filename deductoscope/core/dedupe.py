import logging
import threading
from typing import Dict, List, Optional, Any
from difflib import SequenceMatcher
from .utils import fingerprint, normalize_name,logger
#from engine.py import

class Deduplicator:
    def __init__(self, name_threshold: float = 0.85):
        self.name_threshold = max(0.0, min(1.0, name_threshold))  # CORRIGÉ: clamp
        self._by_fingerprint = {}
        self._lock = threading.Lock()  # AJOUTÉ: thread-
        
    def is_duplicate(self, item: Dict[str, Any]) -> Optional[str]:
        """Vérifie si un item est un doublon"""
        with self._lock:  # AJOUTÉ: protection thread
            key = item.get('key')
            if not key:
                return None
    
            fp = fingerprint(str(key))  # CORRIGÉ: conversion explicite
            if fp in self._by_fingerprint:
                return fp
    
            # Fuzzy name merge if name provided
            name = item.get('name')
            if name:
                norm_name = normalize_name(name)
                for existing_fp, existing in self._by_fingerprint.items():
                    ename = existing.get('name')
                    if ename:
                        norm_ename = normalize_name(ename)
                        if norm_name and norm_ename:  # AJOUTÉ: vérification
                            sim = SequenceMatcher(None, norm_ename, norm_name).ratio()
                            if sim >= self.name_threshold:
                                logger.debug(f"Doublon détecté: {name} ~ {ename} (sim={sim:.2f})")
                                return existing_fp
    
            return None
    
    def add(self, item: Dict[str, Any]) -> str:
        """Ajoute un item et retourne son fingerprint"""
        with self._lock:
            key = item.get('key', '')
            fp = fingerprint(str(key))
            self._by_fingerprint[fp] = item
            return fp
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Retourne tous les items non-dupliqués"""
        with self._lock:
            return list(self._by_fingerprint.values())
    