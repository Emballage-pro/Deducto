import logging
from typing import Any, Dict, Optional

class Scorer:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        # Default weights
        self.w = weights or {
        'source': 0.35,
        'name': 0.30,
        'email': 0.20,
        'geo': 0.05,
        'cross': 0.10,
        }
        # AJOUTÉ: normalise les poids pour qu'ils somment à 1
        total = sum(self.w.values())
        if total > 0:
            self.w = {k: v/total for k, v in self.w.items()}

    def score(self, record: Dict[str, Any]) -> float:
        """Calcule un score de confiance pour un enregistrement"""
        s_source = max(0.0, min(1.0, record.get('source_quality', 0.0)))
        s_name = max(0.0, min(1.0, record.get('name_match', 0.0)))
        s_email = max(0.0, min(1.0, record.get('email_match', 0.0)))
        s_geo = max(0.0, min(1.0, record.get('geo_match', 0.0)))
        cross = min(record.get('cross_count', 0), 5) / 5.0
    
        raw = (
            self.w['source'] * s_source +
            self.w['name'] * s_name +
            self.w['email'] * s_email +
            self.w['geo'] * s_geo +
            self.w['cross'] * cross
        )
    
        return max(0.0, min(1.0, raw))
    