# limiter.py
import time
import threading
import random
import requests
import logging
from typing import Optional, Callable
from functools import wraps
from .config import CONFIG

logger = logging.getLogger("DeductoScope")

# TOKEN BUCKET - RATE LIMITER
class TokenBucket:
    def __init__(self, rate_per_sec: float, capacity: Optional[float] = None):
        self.rate = rate_per_sec
        self.capacity = capacity or rate_per_sec
        self._tokens = self.capacity
        self._last = time.monotonic()
        self._lock = threading.Lock()
    def consume(self, tokens: float = 1.0) -> bool:
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last
            self._last = now
            self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False
    def wait_for_token(self, tokens: float = 1.0):
        """Attend qu'un token soit disponible"""
        while not self.consume(tokens):
            sleep_time = max(0.1, 1.0 / max(1.0, self.rate))  # minimum 100ms
            time.sleep(sleep_time)

# EXPONENTIAL BACKOFF DECORATOR
def backoff_retry(base: float = None, max_attempts: int = None, max_sleep: float = None):
    """
    Décorateur pour retry avec exponential backoff + full jitter
    """
    _base = base if base is not None else CONFIG.get("backoff_base", 1.0)
    _max_attempts = max_attempts if max_attempts is not None else CONFIG.get("backoff_max_attempts", 5)
    _max_sleep = max_sleep if max_sleep is not None else CONFIG.get("backoff_max_sleep", 60.0)

    def deco(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            last_exception = None
            while attempt < _max_attempts:
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    last_exception = e
                    attempt += 1
                    if attempt >= _max_attempts:
                        logger.error(f"Max attempts ({_max_attempts}) reached for {func.__name__}: {e}")
                        raise
                    cap = min(_max_sleep, _base * (2 ** attempt))
                    sleep = random.uniform(0, cap)
                    logger.warning(f"Error in {func.__name__}: {e} — retry {attempt}/{_max_attempts} after {sleep:.2f}s")
                    time.sleep(sleep)
                except Exception as e:
                    # Non-requests exceptions: record and break/raise after attempts
                    last_exception = e
                    attempt += 1
                    if attempt >= _max_attempts:
                        logger.error(f"Max attempts ({_max_attempts}) reached for {func.__name__}: {e}")
                        raise
                    cap = min(_max_sleep, _base * (2 ** attempt))
                    sleep = random.uniform(0, cap)
                    logger.warning(f"Error in {func.__name__}: {e} — retry {attempt}/{_max_attempts} after {sleep:.2f}s")
                    time.sleep(sleep)

            # fallback
            if last_exception:
                raise last_exception
                
        return wrapper
    return deco
