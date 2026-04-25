"""Recherche Brave uniquement"""
import requests
import time
from .config import CONFIG, logger
from .time_out import timeout, TimeoutError
from .limiter import TokenBucket


class BraveSearch:
    """Client pour l'API Brave Search avec rate limiting"""
    
    def __init__(self):
        self.api_key = CONFIG.get('brave_api_key')
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        })
        
        # RATE LIMITER: 0.9 requête par seconde
        rate = CONFIG.get('default_req_per_sec', 1)
        self.rate_limiter = TokenBucket(rate_per_sec=rate)
        
        logger.info(f"BraveSearch initialisé avec rate limit: {rate} req/sec")
    
    @timeout(20, default=[])
    def search(self, query):
        """
        Effectue une recherche web via Brave Search API
        
        Args:
            query: Requête de recherche
            
        Returns:
            Liste de résultats [{title, url, snippet}]
        """
        if not self.api_key:
            logger.error("Brave API key manquante dans config.py")
            return []
        
        # ATTENDRE LE TOKEN (rate limiting)
        self.rate_limiter.wait_for_token()

        #  # DÉLAI FIXE SUPPLÉMENTAIRE (sécurité)
        time.sleep(2.0)  # ← 2 secondes entre chaque requête
        
        url = "https://api.search.brave.com/res/v1/web/search"
        params = {"q": query, "count": 10}
        
        try:
            logger.debug(f"🔍 Requête Brave: {query}")
            response = self.session.get(url, params=params, timeout=15)
            # GESTION SPÉCIFIQUE 429
            if response.status_code == 429:
                logger.error("🚫 RATE LIMIT 429 - Pause de 60 secondes")
                time.sleep(60)
                return []

            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('web', {}).get('results', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('description', '')[:200]
                })
            
            logger.info(f"✅ Brave: {len(results)} résultats pour '{query}'")
            return results
            
        except TimeoutError:
            logger.warning(f"⏱️ Timeout lors de la recherche: {query}")
            return []
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error(f"🚫 RATE LIMIT 429 - Attendez 60 secondes")
                time.sleep(60)  # Attendre 1 minute
                return []
            else:
                logger.error(f"Erreur HTTP Brave ({e.response.status_code}): {e}")
                return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur réseau Brave Search: {e}")
            return []
        except Exception as e:
            logger.error(f"Erreur inattendue Brave Search: {e}")
            return []
    
    def __del__(self):
        """Ferme proprement la session"""
        if hasattr(self, 'session'):
            self.session.close()