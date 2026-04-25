"""
DeductoScope - Outil CLI pour l'analyse et la déduction
"""

__version__ = "0.1.0"

from .cli import main
from .banner import show_banner, load_banner
from .core.IP_DNS import gather_info
from .resources import resource_path
from .core.IP_DNS import save_report

__all__ = [
    "main",
    "show_banner",
    "load_banner",
    "gather_info",
    "resource_path",

    "save_report",
    "logger",
    "CONFIG",
    "DeductoEngine",
    "IdentityGenerator",
    "Scorer",
    "Deduplicator",
    "SimpleSearch",
    "fingerprint",
    "normalize_name",
    
]