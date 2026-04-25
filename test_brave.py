#!/usr/bin/env python3
"""Test avec UNE SEULE requête"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from .deductoscope.core.search import BraveSearch

print("🧪 TEST BRAVE - UNE SEULE REQUÊTE")
print("=" * 60)

brave = BraveSearch()

print("\n⏳ Requête 1: 'test'...")
time.sleep(3)  # Attendre 3 secondes avant la première requête
results = brave.search("test")

if results:
    print(f"✅ {len(results)} résultats")
else:
    print("❌ Aucun résultat ou erreur")

print("\n⏳ Attendez 5 secondes...")
time.sleep(5)

print("\n⏳ Requête 2: 'python'...")
results = brave.search("python")

if results:
    print(f"✅ {len(results)} résultats")
else:
    print("❌ Aucun résultat ou erreur")

print("\n✅ Test terminé")