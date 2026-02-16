#!/usr/bin/env python3
"""
Script de test pour vérifier les nouvelles fonctionnalités
"""

from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from holidays import MarketHolidays
from scraper import TradingEconomicsScraper

def test_holidays():
    """Test de la détection des jours fériés"""
    print("=" * 60)
    print("🧪 TEST: Détection des Jours Fériés")
    print("=" * 60)
    
    # Test 2026
    year = 2026
    print(f"\n📅 Jours Fériés US {year}:")
    us_holidays = MarketHolidays.get_us_holidays(year)
    for date_obj, name in sorted(us_holidays.items()):
        print(f"  {date_obj.strftime('%d/%m/%Y %A')}: {name}")
    
    print(f"\n📅 Jours Fériés UK {year}:")
    uk_holidays = MarketHolidays.get_uk_holidays(year)
    for date_obj, name in sorted(uk_holidays.items()):
        print(f"  {date_obj.strftime('%d/%m/%Y %A')}: {name}")
    
    # Test jours spécifiques
    print("\n🔍 Test de dates spécifiques:")
    test_dates = [
        date(2026, 1, 1),   # New Year
        date(2026, 7, 4),   # Independence Day
        date(2026, 12, 25), # Christmas
        date(2026, 1, 19),  # MLK Day (3rd Monday)
        date(2026, 5, 25),  # Memorial Day (last Monday)
    ]
    
    for test_date in test_dates:
        holidays = MarketHolidays.is_market_holiday(test_date)
        if holidays:
            print(f"  ✅ {test_date}: {', '.join(holidays)}")
        else:
            print(f"  ❌ {test_date}: Pas de jour férié")
    
    # Test prochains jours fériés
    print("\n📆 Prochains jours fériés (30 jours):")
    upcoming = MarketHolidays.get_upcoming_holidays(days_ahead=30)
    if upcoming:
        for holiday_info in upcoming:
            date_str = holiday_info['date'].strftime('%d/%m/%Y %A')
            holidays_str = ' & '.join(holiday_info['holidays'])
            print(f"  🔴 {date_str}: {holidays_str}")
    else:
        print("  ➡️ Aucun jour férié dans les 30 prochains jours")

def test_scraper():
    """Test du scraper amélioré"""
    print("\n" + "=" * 60)
    print("🧪 TEST: Scraper TradingEconomics")
    print("=" * 60)
    
    print("\n📡 Mots-clés de recherche (événements pertinents):")
    relevant_keywords = [
        'interest rate', 'fomc', 'fed funds',
        'cpi', 'ppi', 'pce', 'core cpi',
        'retail sales', 'unemployment',
        'nfp', 'payroll', 'gdp',
        'ecb', 'boe'
    ]
    
    for keyword in relevant_keywords:
        print(f"  ✅ {keyword}")
    
    print("\n🔄 Test de connexion à TradingEconomics...")
    scraper = TradingEconomicsScraper()
    
    # Test avec des événements fictifs
    test_events = [
        "CPI m/m",
        "Core CPI y/y",
        "Producer Price Index",
        "Personal Consumption Expenditures",
        "Retail Sales m/m",
        "Fed Interest Rate Decision",
        "Non Farm Payrolls",
        "Unemployment Rate",
        "ECB Interest Rate Decision",
        "BoE Interest Rate Decision",
        "ISM Manufacturing PMI"
    ]
    
    print("\n🎯 Test de détection d'événements:")
    for event in test_events:
        is_relevant = scraper._is_relevant_event(event)
        simplified = scraper._simplify_event_name(event)
        assets = scraper._get_affected_assets(event)
        
        if is_relevant:
            print(f"  ✅ {event}")
            print(f"     → Simplifié: {simplified}")
            print(f"     → Assets: {', '.join(assets[:5])}")
        else:
            print(f"  ❌ {event} (non détecté)")

def test_date_utilities():
    """Test des fonctions utilitaires de date"""
    print("\n" + "=" * 60)
    print("🧪 TEST: Fonctions Utilitaires")
    print("=" * 60)
    
    from utils import is_trading_day, get_next_trading_day
    
    today = datetime.now(ZoneInfo("UTC")).date()
    
    print(f"\n📅 Aujourd'hui: {today.strftime('%d/%m/%Y %A')}")
    print(f"  Est un jour de trading: {is_trading_day(today)}")
    
    print("\n🔍 Test des 7 prochains jours:")
    for i in range(7):
        check_date = today + timedelta(days=i)
        is_trading = is_trading_day(check_date)
        holidays = MarketHolidays.is_market_holiday(check_date)
        
        status = "✅ TRADING" if is_trading else "❌ FERMÉ"
        holiday_info = f" ({', '.join(holidays)})" if holidays else ""
        
        print(f"  {check_date.strftime('%d/%m/%Y %A')}: {status}{holiday_info}")
    
    next_trading = get_next_trading_day()
    if next_trading:
        print(f"\n➡️ Prochain jour de trading: {next_trading.strftime('%d/%m/%Y %A')}")

def main():
    """Exécute tous les tests"""
    print("\n" + "🚀" * 30)
    print("TESTS DES NOUVELLES FONCTIONNALITÉS DU BOT")
    print("🚀" * 30 + "\n")
    
    try:
        test_holidays()
        test_scraper()
        test_date_utilities()
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS TERMINÉS")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
