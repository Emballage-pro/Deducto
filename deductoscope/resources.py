import sys
from pathlib import Path


def resource_path(*parts):
    """
    Retourne le chemin vers une ressource.
    Fonctionne en dev, package installé, et PyInstaller (_MEIPASS).
    """
    # Works in dev, installed package, and PyInstaller (_MEIPASS)
    if getattr(sys, "_MEIPASS", None):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent
    return base.joinpath(*parts)