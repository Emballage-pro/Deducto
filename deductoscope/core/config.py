import logging
import os
from dotenv import load_dotenv

load_dotenv

CONFIG = {
"brave_api_key": os.getenv("BRAVE_API_KEY"), 
"results_dir": "results",
"max_workers": 1,          # CORRIGÉ: réduit pour éviter rate limit
"default_req_per_sec": 1,  # CORRIGÉ: plus conservateur
"backoff_base": 2.0,       # CORRIGÉ: augmenté
"backoff_max_attempts": 3,
"backoff_max_sleep": 60.0,
"request_timeout": 15,     # AJOUTÉ: timeout explicite
"max_attempts": 5,
"max_sleep": 60.0,
"base": 1.0, #?
}
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("deducto")