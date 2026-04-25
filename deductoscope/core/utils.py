import unicodedata
import hashlib
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)
def save_json(obj: Any, path: str):
    """Sauvegarde un objet en JSON avec gestion d'erreur"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            logger.info(f"Fichier sauvegardé: {path}")
    except IOError as e:# verif indentation 
        logger.error(f"Erreur lors de la sauvegarde de {path}: {e}")
        raise
def fingerprint(s: str) -> str:
    """Génère un hash SHA-256 d'une chaîne"""
    if not s:
        s = "empty"
    return hashlib.sha256(s.encode("utf-8")).hexdigest()  
def normalize_name(s: str) -> str:
    """Normalise un nom pour la comparaison"""
    if not s:  # AJOUTÉ: gestion des None
        return ""
    s = s.strip().lower()
    # Normaliser les caractères avec accents
    # NFKD = décompose les accents (é → e + ´)
    s = unicodedata.normalize("NFKD", s)
    # Supprimer les diacritiques (accents)
    # combining() = vrai si c'est un accent
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    # Nettoyer les espaces multiples
    s = " ".join(s.split())
    return s
