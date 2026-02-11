from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def get_first_friday_of_month(year, month):
    """Retourne le 1er vendredi du mois donné"""
    first_day = datetime(year, month, 1, tzinfo=ZoneInfo("America/New_York"))
    days_until_friday = (4 - first_day.weekday()) % 7
    first_friday = first_day + timedelta(days=days_until_friday)
    return first_friday

def get_all_wednesdays_of_month(year, month):
    """Retourne tous les mercredis du mois"""
    first_day = datetime(year, month, 1, tzinfo=ZoneInfo("America/New_York"))
    days_until_wednesday = (2 - first_day.weekday()) % 7
    first_wednesday = first_day + timedelta(days=days_until_wednesday)
    
    wednesdays = []
    current = first_wednesday
    while current.month == month:
        wednesdays.append(current)
        current += timedelta(days=7)
    
    return wednesdays

def convert_est_to_paris(dt_est):
    """Convertit datetime EST vers Paris"""
    dt_utc = dt_est.astimezone(ZoneInfo("UTC"))
    dt_paris = dt_utc.astimezone(ZoneInfo("Europe/Paris"))
    return dt_paris

def is_earnings_season():
    """Vérifie si on est en période d'earnings"""
    today = datetime.now(ZoneInfo("Europe/Paris"))
    year = today.year
    
    earnings_periods = [
        (datetime(year, 1, 15, tzinfo=ZoneInfo("Europe/Paris")), 
         datetime(year, 2, 5, tzinfo=ZoneInfo("Europe/Paris"))),
        (datetime(year, 4, 15, tzinfo=ZoneInfo("Europe/Paris")), 
         datetime(year, 5, 5, tzinfo=ZoneInfo("Europe/Paris"))),
        (datetime(year, 7, 15, tzinfo=ZoneInfo("Europe/Paris")), 
         datetime(year, 8, 5, tzinfo=ZoneInfo("Europe/Paris"))),
        (datetime(year, 10, 15, tzinfo=ZoneInfo("Europe/Paris")), 
         datetime(year, 11, 5, tzinfo=ZoneInfo("Europe/Paris"))),
    ]
    
    for start, end in earnings_periods:
        if start <= today <= end:
            return True, start, end
    
    return False, None, None

def get_hardcoded_events():
    """Retourne les événements hardcodés pour le mois en cours"""
    now = datetime.now(ZoneInfo("Europe/Paris"))
    year = now.year
    month = now.month
    
    events = {}
    
    # NFP - 1er vendredi du mois
    nfp_date = get_first_friday_of_month(year, month)
    nfp_date = nfp_date.replace(hour=13, minute=30)
    nfp_paris = convert_est_to_paris(nfp_date)
    
    events[nfp_paris.date().isoformat()] = {
        "name": "NFP - Non-Farm Payroll",
        "time_paris": nfp_paris.strftime("%H:%M"),
        "country": "🇺🇸",
        "importance": "⭐⭐⭐⭐⭐",
        "assets": ["ES", "NQ", "GC", "6E", "CL", "BTC", "ETH"],
        "description": "Nombre d'emplois créés USA - Annonce critique"
    }
    
    # Oil Inventory - Tous les mercredis
    wednesdays = get_all_wednesdays_of_month(year, month)
    for wednesday in wednesdays:
        oil_date = wednesday.replace(hour=10, minute=30)
        oil_paris = convert_est_to_paris(oil_date)
        
        if oil_paris.date() >= now.date():
            events[oil_paris.date().isoformat()] = {
                "name": "EIA Crude Oil Inventories",
                "time_paris": oil_paris.strftime("%H:%M"),
                "country": "🇺🇸",
                "importance": "⭐⭐⭐⭐",
                "assets": ["CL", "ES", "GC"],
                "description": "Stocks de pétrole brut USA"
            }
    
    # Earnings Season
    is_earnings, earnings_start, earnings_end = is_earnings_season()
    if is_earnings:
        earnings_key = earnings_start.date().isoformat()
        if earnings_key not in events:
            events[earnings_key] = {
                "name": "Earnings Season",
                "time_paris": "Variable",
                "country": "🇺🇸",
                "importance": "⭐⭐⭐⭐",
                "assets": ["NQ", "ES", "BTC", "ETH"],
                "description": f"Période des résultats trimestriels jusqu'au {earnings_end.strftime('%d/%m')}"
            }
    
    return events
