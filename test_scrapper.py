#!/usr/bin/env python3
"""
Script de diagnostic du scraper TradingEconomics
"""

import sys
sys.path.insert(0, '/mnt/user-data/outputs')

from scraper import TradingEconomicsScraper
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def test_direct_request():
    """Test direct de la requête HTTP"""
    print("=" * 60)
    print("🧪 TEST 1: Requête HTTP directe")
    print("=" * 60)
    
    url = "https://tradingeconomics.com/calendar"
    today = datetime.now(ZoneInfo("UTC"))
    end_date = today + timedelta(days=7)
    
    params = {
        'd1': today.strftime('%Y-%m-%d'),
        'd2': end_date.strftime('%Y-%m-%d')
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"📍 URL: {url}")
    print(f"📅 Période: {params['d1']} → {params['d2']}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Content Length: {len(response.content):,} bytes")
        print(f"📝 Content Type: {response.headers.get('content-type', 'N/A')}")
        
        # Vérifier si on a du HTML
        if 'text/html' in response.headers.get('content-type', ''):
            print("✅ Type de contenu: HTML")
        else:
            print("⚠️ Type de contenu inattendu")
        
        return response
        
    except Exception as e:
        print(f"❌ Erreur requête: {e}")
        return None

def test_html_parsing(response):
    """Test du parsing HTML"""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Parsing HTML")
    print("=" * 60)
    
    if not response:
        print("❌ Pas de réponse à parser")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Chercher la table calendar
    calendar_table = soup.find('table', {'id': 'calendar'})
    print(f"Table 'calendar': {'✅ Trouvée' if calendar_table else '❌ Introuvable'}")
    
    if calendar_table:
        tbody = calendar_table.find('tbody')
        print(f"Tbody: {'✅ Trouvé' if tbody else '❌ Introuvable'}")
        
        if tbody:
            rows = tbody.find_all('tr')
            print(f"Nombre de lignes: {len(rows)}")
            
            # Afficher les 3 premières lignes pour debug
            print("\n📋 Premières lignes:")
            for i, row in enumerate(rows[:3]):
                classes = row.get('class', [])
                print(f"  Ligne {i}: classes={classes}")
                cells = row.find_all('td')
                print(f"    → {len(cells)} cellules")
        else:
            print("\n⚠️ Structure de la table:")
            print(f"  Tag de la table: {calendar_table.name}")
            print(f"  Enfants directs: {[child.name for child in calendar_table.children if hasattr(child, 'name')]}")
    else:
        # Chercher d'autres tables possibles
        print("\n🔍 Recherche d'autres tables:")
        all_tables = soup.find_all('table')
        print(f"  Total de tables trouvées: {len(all_tables)}")
        
        for i, table in enumerate(all_tables[:3]):
            table_id = table.get('id', 'N/A')
            table_class = table.get('class', [])
            print(f"  Table {i}: id='{table_id}', class={table_class}")

def test_scraper_class():
    """Test de la classe TradingEconomicsScraper"""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Classe TradingEconomicsScraper")
    print("=" * 60)
    
    scraper = TradingEconomicsScraper()
    events = scraper.get_calendar_events(days_ahead=7)
    
    print(f"\n📊 Résultat:")
    print(f"  Nombre d'événements: {len(events)}")
    
    if events:
        print("\n✅ Événements trouvés:")
        for date_key, event in sorted(events.items()):
            print(f"\n  📅 {date_key}")
            print(f"     {event['country']} {event['name']}")
            print(f"     ⏰ {event['time_paris']} - {event['importance']}")
    else:
        print("\n❌ Aucun événement trouvé")

def main():
    print("\n" + "🚀" * 30)
    print("DIAGNOSTIC SCRAPER TRADINGECONOMICS")
    print("🚀" * 30 + "\n")
    
    # Test 1: Requête HTTP
    response = test_direct_request()
    
    # Test 2: Parsing HTML
    if response:
        test_html_parsing(response)
    
    # Test 3: Classe scraper
    test_scraper_class()
    
    print("\n" + "=" * 60)
    print("✅ DIAGNOSTIC TERMINÉ")
    print("=" * 60)

if __name__ == "__main__":
    main()
