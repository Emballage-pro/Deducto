# deductoscope/core/__init__.py
"""
DeductoScope Core Module
"""

# Importer depuis IP_DNS.py (qui contient save_report)
from .IP_DNS import (
    get_dns,
    get_whois,
    get_http_info,
    get_crtsh,
    gather_info,
    save_report
)

# Importer depuis engine.py
from .engine import DeductoEngine

# Importer depuis config.py
from .config import CONFIG, logger

# Importer depuis utils.py
from .utils import save_json, fingerprint, normalize_name

# Importer depuis identity.py
from .identity import IdentityGenerator

# Importer depuis scoring.py
from .scoring import Scorer

# Importer depuis dedupe.py
from .dedupe import Deduplicator

# Importer depuis search.py
from .search import BraveSearch

__all__ = [
    # IP_DNS
    'get_dns',
    'get_whois',
    'get_http_info',
    'get_crtsh',
    'gather_info',
    'save_report',
    
    # Engine
    'DeductoEngine',
    
    # Config
    'CONFIG',
    'logger',
    
    # Utils
    'save_json',
    'fingerprint',
    'normalize_name',
    
    # Identity
    'IdentityGenerator',
    
    # Scoring
    'Scorer',
    
    # Dedupe
    'Deduplicator',
    
    # Search
    'BraveSearch',
]