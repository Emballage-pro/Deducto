"""Gestion des timeouts"""
import functools
import threading

class TimeoutError(Exception):
    pass

def timeout(seconds: int, default=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = [default]
            exception = [None] 
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            if thread.is_alive():
                raise TimeoutError(f"Timeout après {seconds}s")
            if exception[0]:
                raise exception[0]
            return result[0]
        return wrapper
    return decorator