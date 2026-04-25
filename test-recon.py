#!/usr/bin/env python3
"""Test minimal de recon"""
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from deductoscope.core.engine import DeductoEngine
from deductoscope.core.utils import save_json

def test_recon():
    """Test basique de reconnaissance"""
    print("=" * 60)
    print("🧪 TEST DE RECONNAISSANCE")
    print("=" * 60)
    
    first = "John"
    last = "Doe"
    
    print(f"\n🎯 Cible: {first} {last}")
    
    try:
        print("\n⏳ Étape 1: Initialisation du moteur...")
        with DeductoEngine() as engine:
            print("   ✅ Moteur créé")
            
            print("\n⏳ Étape 2: Génération des usernames...")
            from deductoscope.core.identity import IdentityGenerator
            usernames = IdentityGenerator.generate_usernames(first, last)
            print(f"   ✅ {len(usernames)} usernames générés: {usernames[:3]}...")
            
            #print("\n⏳ Étape 3: Test recherche GitHub (1 username seulement)...")
            #try:
            #    res = engine.search.github_search_user(usernames[0])
            #    print(f"   ✅ GitHub OK - {len(res.get('items', []))} résultats")
            #except Exception as e:
            #    print(f"   ⚠️ GitHub échoué: {e}")
            
            print("\n⏳ Étape 4: Lancement de la recherche complète...")
            print("   (Ceci peut prendre 30-60 secondes)")
            
            results = engine.run_recon(first, last)
            
            print(f"\n✅ SUCCÈS!")
            print(f"   📊 {len(results['results'])} résultats trouvés")
            print(f"   ⏱️  Durée: {results['metadata']['duration']:.1f}s")
            
            # Sauvegarder
            output = "test_recon_output.json"
            save_json(results, output)
            print(f"   💾 Sauvegardé dans: {output}")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Interruption par l'utilisateur (Ctrl+C)")
        return 1
    
    except Exception as e:
        print("\n\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(test_recon())