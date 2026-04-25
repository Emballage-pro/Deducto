from .resources import resource_path
from colorama import Fore, Style, init
import time
import sys

# Initialiser colorama
init(autoreset=True)


def load_banner(name):
    """Charge un fichier banner depuis le dossier banners/"""
    path = resource_path("banners", f"{name}.txt")
    return path.read_text(encoding="utf-8")


def show_banner(name, rainbow=False, no_anim=False):
    """Affiche le banner avec options de couleur et animation"""
    banner_text = load_banner(name)
    
    if rainbow:
        colors = [Fore.GREEN]
        lines = banner_text.split('\n')
        #COLORS
        for i, line in enumerate(lines):
            color = colors[i % len(colors)]
            print(color + line)
            
            # Animation sauf si désactivée
            if not no_anim:
                time.sleep(0.05)
    else:
        # Affichage simple sans couleur
        if no_anim:
            print(banner_text)
        else:
            for line in banner_text.split('\n'):
                print(line)
                time.sleep(0.05)
    
    print(Style.RESET_ALL)
    '''
    COLORS #rainbow color : [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    blue colors = [Fore.CYAN, Fore.BLUE, Fore.CYAN, Fore.BLUE]
    colors = [Fore.GREEN]
    colors = [Fore.GREEN, Fore.CYAN, Fore.GREEN, Fore.CYAN]
    '''
    