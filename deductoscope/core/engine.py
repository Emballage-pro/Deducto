"""Moteur principal de DeductoScope"""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional, Any
from difflib import SequenceMatcher

from .config import CONFIG, logger
from .identity import IdentityGenerator
from .search import BraveSearch
from .dedupe import Deduplicator
from .scoring import Scorer
from .utils import normalize_name, save_json


SEARCH_QUERIES = [
    #'site:linkedin.com/in "{name}" '
    '"{name}" ("linkedin" OR "linkedin.com")'
]


class DeductoEngine:
    """Moteur principal de DeductoScope"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialise le moteur avec la configuration"""
        self.config = config or CONFIG
        self.brave = BraveSearch()
        self.dedupe = Deduplicator()
        self.scorer = Scorer()
        self.executor = ThreadPoolExecutor(
            max_workers=self.config.get('max_workers', 3),
            thread_name_prefix="deducto"
        )
        logger.info("DeductoEngine initialisé")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ferme proprement les ressources"""
        logger.info("🔄 Fermeture du DeductoEngine...")
        self.executor.shutdown(wait=True)
        logger.info("✅ Resources fermées proprement")
        return False

    def enrich_and_store(self, raw: Dict[str, Any], target: Dict[str, str]) -> Optional[str]:
        """
        Enrichit et stocke un résultat brut
        
        Args:
            raw: Données brutes du résultat
            target: Cible de la recherche (first, last, email, city)
            
        Returns:
            Fingerprint du résultat stocké, ou None en cas d'erreur
        """
        try:
            rec = {}
            rec['source'] = raw.get('source', 'unknown')
            rec['source_quality'] = raw.get('source_quality', 0.5)
            rec['title'] = raw.get('title', '')
            rec['url'] = raw.get('url', '')
            rec['snippet'] = raw.get('snippet', '')[:500]
            
            # Clé unique pour déduplication
            rec['key'] = rec['url'] or f"unknown_{time.time()}"
            
            # Calcul du score de correspondance avec le nom
            tname = f"{target.get('first','')} {target.get('last','')}".strip()
            rec['name_match'] = 0.0
            
            if rec['title']:
                sim = SequenceMatcher(
                    None,
                    normalize_name(rec['title']),
                    normalize_name(tname)
                ).ratio()
                rec['name_match'] = sim
            
            # Correspondance email
            rec['email_match'] = 0.0
            if target.get('email') and rec['snippet']:
                if target['email'].lower() in rec['snippet'].lower():
                    rec['email_match'] = 1.0
            
            # Correspondance géographique
            rec['geo_match'] = 0.0
            if target.get('city') and rec['snippet']:
                if target['city'].lower() in rec['snippet'].lower():
                    rec['geo_match'] = 1.0
            
            rec['cross_count'] = raw.get('cross_count', 0)
            rec['score'] = self.scorer.score(rec)
            rec['timestamp'] = time.time()
            
            # Déduplication
            dup_fp = self.dedupe.is_duplicate(rec)
            if dup_fp:
                existing = self.dedupe._by_fingerprint.get(dup_fp)
                if existing and rec['score'] > existing.get('score', 0):
                    logger.debug(f"Mise à jour doublon: {rec['key']}")
                    self.dedupe._by_fingerprint[dup_fp].update(rec)
                return dup_fp
            else:
                return self.dedupe.add(rec)
                
        except Exception as e:
            logger.error(f"Erreur enrichissement: {e}")
            return None

    def run_recon(self, first: str, last: str, hints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Lance la reconnaissance OSINT complète
        
        Args:
            first: Prénom
            last: Nom
            hints: Indices optionnels (email, city, year)
            
        Returns:
            Dictionnaire contenant les résultats et métadonnées
        """
        hints = hints or {}
        target = {
            "first": first,
            "last": last,
            "email": hints.get('email'),
            "city": hints.get('city')
        }
        
        out = {
            "target": target,
            "results": [],
            "metadata": {
                "start_time": time.time(),
                "version": "1.0-brave"
            }
        }
        
        # Génération des usernames
        usernames = IdentityGenerator.generate_usernames(
            first, last, year=hints.get('year')
        )
        out['usernames'] = usernames
        logger.info(f"Usernames générés: {len(usernames)}")
        
        # Lancement des recherches
        futures = []
        full_name = f"{first} {last}"
        
        for query_template in SEARCH_QUERIES:
            query = query_template.format(name=full_name)
            futures.append(
                self.executor.submit(self._search_and_process_brave, query, target)
            )
        
        # Attente de completion
        completed = 0
        failed = 0
        
        for f in as_completed(futures):
            try:
                f.result()
                completed += 1
            except Exception as e:
                failed += 1
                logger.error(f"Task failed: {e}")
        
        logger.info(f"Tâches complétées: {completed}/{len(futures)} (échecs: {failed})")
        
        # Compilation des résultats
        out['results'] = sorted(
            self.dedupe.get_all(),
            key=lambda x: x.get('score', 0),
            reverse=True
        )
        
        out['metadata']['end_time'] = time.time()
        out['metadata']['duration'] = out['metadata']['end_time'] - out['metadata']['start_time']
        out['metadata']['result_count'] = len(out['results'])
        
        return out

    def _search_and_process_brave(self, query: str, target: Dict[str, Any]):
        
        try:
            logger.info(f"🔍 Recherche Brave: {query}")
            results = self.brave.search(query)
            
            if results:
                logger.info(f"  → {len(results)} résultats trouvés")
            
            for item in results:
                raw = {
                    'source': 'brave',
                    'source_quality': 0.75,
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('snippet', ''),
                    'cross_count': 1,
                }
                self.enrich_and_store(raw, target)
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur recherche Brave: {e}")