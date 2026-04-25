#!/usr/bin/env python3
"""
DeductoScope CLI - Interface en ligne de commande
"""
import argparse
import sys
import json
from pathlib import Path

from .banner import show_banner
from .core.IP_DNS import gather_info, save_report
from .core.engine import DeductoEngine
from .core.utils import save_json


def main():
    """Point d'entrée principal du CLI"""
    parser = argparse.ArgumentParser(
        prog="deductoscope",
        description="🔎 DeductoScope CLI - outil d'information gathering automatisé",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # ==================================================================
    # COMMANDE: domain (analyse de domaine/IP)
    # ==================================================================
    domain_parser = subparsers.add_parser(
        'domain',
        help='Analyse un domaine ou une IP'
    )
    domain_parser.add_argument(
        "target",
        help="IP ou hostname à analyser"
    )
    domain_parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Ne pas afficher le banner"
    )
    domain_parser.add_argument(
        "--no-anim",
        action="store_true",
        help="Désactive les animations"
    )
    
    # ==================================================================
    # COMMANDE: recon (recherche de personne)
    # ==================================================================
    recon_parser = subparsers.add_parser(
        'recon',
        help='Recherche OSINT sur une personne'
    )
    recon_parser.add_argument('first', help='Prénom')
    recon_parser.add_argument('last', help='Nom')
    recon_parser.add_argument('--email', help='Email (optionnel)')
    recon_parser.add_argument('--city', help='Ville (optionnel)')
    recon_parser.add_argument('--year', help='Année (optionnel)')
    recon_parser.add_argument(
        '--output', '-o',
        help='Fichier de sortie JSON'
    )
    recon_parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Ne pas afficher le banner"
    )
    
    args = parser.parse_args()
    
    # Si aucune commande, afficher l'aide
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Afficher le banner (si demandé)
    if not getattr(args, 'no_banner', False):
        show_banner("deductoscope", rainbow=True, no_anim=getattr(args, 'no_anim', False))
    
    try:
        # ==============================================================
        # TRAITEMENT: domain
        # ==============================================================
        if args.command == 'domain':
            result = gather_info(args.target, no_anim=args.no_anim)
            print(f"\n✅ Analyse terminée pour: {args.target}")
        
        # ==============================================================
        # TRAITEMENT: recon
        # ==============================================================
        elif args.command == 'recon':
            hints = {}
            if args.email:
                hints['email'] = args.email
            if args.city:
                hints['city'] = args.city
            if args.year:
                hints['year'] = args.year
            
            print(f"🔍 Reconnaissance pour: {args.first} {args.last}")
            
            with DeductoEngine() as engine:
                results = engine.run_recon(args.first, args.last, hints)
            
            # Sauvegarder les résultats
            if args.output:
                output_path = args.output
            else:
                Path("results").mkdir(exist_ok=True)
                output_path = f"results/recon_{args.first}_{args.last}.json"
            
            save_json(results, output_path)
            
            print(f"✅ Résultats sauvegardés: {output_path}")
            print(f"📊 {len(results['results'])} résultats trouvés")
    
    except KeyboardInterrupt:
        print("\n⚠️ Interruption utilisateur", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Erreur: {e}", file=sys.stderr)
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()