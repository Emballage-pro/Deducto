import logging
from typing import List, Optional

logger = logging.getLogger("DeductoScope") #code à reverifier

class IdentityGenerator:
    @staticmethod
    def generate_usernames(first: str, last: str, year: Optional[str] = None) -> List[str]:
        """Génère des variations de noms d'utilisateur"""
        if not first or not last:  # AJOUTÉ: validation
            logger.warning("Prénom ou nom manquant pour la génération de usernames")
            return []
        f = first.lower().strip()
        l = last.lower().strip()

        opts = [
        f"{f}.{l}", f"{f}{l}", f"{f[0]}{l}", f"{f}_{l}",
        f"{l}{f}", f"{l}.{f}", f"{f}{l[0]}", f"{f[0]}.{l}",
        ]

        if year and year.isdigit():  # CORRIGÉ: validation de l'année
            opts += [f"{f}{year}", f"{f}.{l}{year}", f"{f}{l}{year}"]

        # Remove duplicates and clean
        clean = []
        for u in opts:
            u2 = ''.join(c for c in u if c.isalnum() or c in ['.', '_'])
            if u2 and u2 not in clean:  # AJOUTÉ: vérification non-vide
                clean.append(u2)
        return clean

    @staticmethod
    def generate_emails(first: str, last: str, domain_guesses: List[str]) -> List[str]:
        """Génère des variations d'emails"""
        if not domain_guesses:  # AJOUTÉ: validation
            return []

        usernames = IdentityGenerator.generate_usernames(first, last)
        emails = []
        for d in domain_guesses:
            d_clean = d.strip().lower()
            if not d_clean:
                continue
            for u in usernames:
                emails.append(f"{u}@{d_clean}")

        return list(dict.fromkeys(emails))  # Déduplique en préservant l'ordre
