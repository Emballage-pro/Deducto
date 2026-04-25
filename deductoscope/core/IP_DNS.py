#!/usr/bin/env python3
"""
Module core de DeductoScope - Collecte d'informations OSINT
"""
import os
import time
import json
from pathlib import Path

try:
    import requests
    import dns.resolver
    import whois
    from bs4 import BeautifulSoup
    from urllib.parse import quote_plus
except ImportError as e:
    print(f"⚠️  Dépendance manquante : {e.name}")
    print("Installez les dépendances avec : pip install requests dnspython python-whois beautifulsoup4")
    raise


def get_dns(domain):
    """Récupère les enregistrements DNS."""
    records = {}
    types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
    for t in types:
        try:
            ans = dns.resolver.resolve(domain, t, lifetime=5)
            records[t] = [r.to_text() for r in ans]
        except dns.resolver.NXDOMAIN:
            records[t] = {"error": "Domain does not exist"}
        except dns.resolver.NoAnswer:
            records[t] = []
        except Exception as e:
            records[t] = {"error": str(e)}
    return records


def get_whois(domain):
    """Récupère les informations WHOIS."""
    try:
        w = whois.whois(domain)
        result = {}
        for key, value in w.items():
            if isinstance(value, (list, tuple)):
                result[key] = [str(v) for v in value]
            else:
                result[key] = str(value) if value is not None else None
        return result
    except Exception as e:
        return {"error": str(e)}


def get_http_info(domain):
    """Récupère les informations HTTP et le titre de la page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (DeductoScope OSINT Tool)'
    }
    
    for protocol in ["https", "http"]:
        url = f"{protocol}://{domain}"
        try:
            r = requests.get(url, timeout=8, allow_redirects=True, 
                           headers=headers, verify=True)
            
            title = None
            if 'text/html' in r.headers.get('Content-Type', ''):
                soup = BeautifulSoup(r.text, 'html.parser')
                title_tag = soup.find('title')
                title = title_tag.string.strip() if title_tag else None
            
            return {
                "url": r.url,
                "status_code": r.status_code,
                "headers": dict(r.headers),
                "title": title,
                "protocol": protocol
            }
        except requests.exceptions.SSLError:
            if protocol == "https":
                continue
            return {"error": "SSL Error"}
        except Exception as e:
            if protocol == "http":
                return {"error": str(e)}
    
    return {"error": "Unable to connect"}


def get_crtsh(domain):
    """Interroge crt.sh pour les certificats SSL."""
    q = quote_plus(f"%.{domain}")
    url = f"https://crt.sh/?q={q}&output=json"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            seen = set()
            unique = []
            for cert in data[:100]:
                name = cert.get('name_value')
                if name and name not in seen:
                    seen.add(name)
                    unique.append({
                        'name': name,
                        'issued': cert.get('entry_timestamp')
                    })
            return unique
        return {"error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def gather_info(target, no_anim=False):
    """
    Collecte des informations OSINT sur une cible (domaine ou IP).
    
    Args:
        target: Domaine ou IP à analyser
        no_anim: Si True, désactive les délais d'animation
        
    Returns:
        dict: Dictionnaire contenant toutes les informations collectées
    """
    domain = target.lower().strip()
    delay = 0 if no_anim else 1
    
    result = {
        "domain": domain,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print(f"\n[*] Collecte d'informations pour : {domain}")
    
    print("[*] Enregistrements DNS...")
    result["dns"] = get_dns(domain)
    time.sleep(delay)
    
    print("[*] Informations WHOIS...")
    result["whois"] = get_whois(domain)
    time.sleep(delay)
    
    print("[*] Informations HTTP...")
    result["http"] = get_http_info(domain)
    time.sleep(delay)
    
    print("[*] Certificats SSL (crt.sh)...")
    result["crtsh"] = get_crtsh(domain)
    
    print("\n✓ Enquête terminée !")
    
    # Sauvegarder le rapport
    save_report(result, domain)
    
    return result


def save_report(data, domain):
    """Sauvegarde le rapport en JSON sans affichage dans le CMD."""
    outdir = "reports" #gpt
    os.makedirs(outdir, exist_ok=True) #gpt
    filename = os.path.join(outdir, f"report_{domain}_{int(time.time())}.json") #gpt
    #filename = f"report_{domain}_{int(time.time())}.json"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        #print(f"📄 Rapport sauvegardé : {filename}")
    except Exception as e:
        print(f"✗ Erreur lors de la sauvegarde : {e}")
    return    

##########################################################################
# FIN DU MODULE
##########################################################################