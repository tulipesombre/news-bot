from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from holidays import MarketHolidays

def format_event_message(event):
    """Formate un événement en message Discord élégant"""
    assets_str = " ".join(event['assets'][:5])  # Limiter à 5 assets
    
    message = f"""
╔══════════════════════════════════
║ **{event['name']}**
║ 
║ 🕐 **Heure:** {event['time_paris']} (Paris)
║ {event['country']} **Impact:** {event['importance']}
║ 📊 **Assets:** `{assets_str}`
╚══════════════════════════════════
"""
    return message.strip()

def format_weekly_agenda(events_by_date):
    """Formate l'agenda hebdomadaire avec détection des jours fériés"""
    if not events_by_date:
        return "📅 **Aucun événement majeur cette semaine**"
    
    message = "📅 **AGENDA ÉCONOMIQUE - 7 PROCHAINS JOURS**\n\n"
    
    sorted_dates = sorted(events_by_date.keys())
    
    for date_str in sorted_dates:
        event = events_by_date[date_str]
        date_obj = datetime.fromisoformat(date_str)
        
        # Vérifier si c'est un jour férié
        holidays = MarketHolidays.is_market_holiday(date_obj.date())
        
        day_name = date_obj.strftime('%A %d %B').capitalize()
        
        # Ajouter un indicateur si jour férié
        holiday_indicator = ""
        if holidays:
            holiday_names = " | ".join(holidays)
            holiday_indicator = f"\n🔴 **JOUR FÉRIÉ:** {holiday_names}"
        
        message += f"**{day_name}**{holiday_indicator}\n"
        message += f"🕐 {event['time_paris']} | {event['country']} {event['importance']}\n"
        message += f"**{event['name']}**\n"
        message += f"📊 Assets: `{' '.join(event['assets'][:5])}`\n\n"
    
    # Ajouter section des jours fériés à venir
    upcoming_holidays = MarketHolidays.get_upcoming_holidays(days_ahead=7)
    if upcoming_holidays:
        message += "\n━━━━━━━━━━━━━━━━━━━━\n"
        message += "🚨 **JOURS FÉRIÉS CETTE SEMAINE** 🚨\n"
        for holiday_info in upcoming_holidays:
            date_str = holiday_info['date'].strftime('%A %d %B').capitalize()
            holidays_str = " & ".join(holiday_info['holidays'])
            message += f"• **{date_str}:** {holidays_str}\n"
    
    message += "\n━━━━━━━━━━━━━━━━━━━━"
    message += "\n⚠️ **Les marchés peuvent être fermés ou avoir des horaires réduits les jours fériés**"
    
    return message

def format_daily_reminder(event):
    """Formate le rappel du jour avec indication de jour férié"""
    date_obj = event['datetime'].date()
    holidays = MarketHolidays.is_market_holiday(date_obj)
    
    holiday_warning = ""
    if holidays:
        holiday_names = " | ".join(holidays)
        holiday_warning = f"\n\n🔴 **ATTENTION: JOUR FÉRIÉ**\n{holiday_names}\n⚠️ Marchés potentiellement fermés ou volatilité réduite"
    
    message = f"""
🚨 **RAPPEL ÉVÉNEMENT MAJEUR AUJOURD'HUI** 🚨

**{event['name']}**
🕐 Dans ~1h ({event['time_paris']} Paris)
{event['country']} Impact: {event['importance']}
📊 Assets concernés: `{' '.join(event['assets'][:5])}`
{holiday_warning}

⚡ Préparez vos positions!
"""
    return message.strip()

def get_next_trading_day():
    """Retourne le prochain jour ouvrable (non férié)"""
    today = datetime.now(ZoneInfo("UTC")).date()
    
    for i in range(1, 30):  # Chercher jusqu'à 30 jours dans le futur
        check_date = today + timedelta(days=i)
        
        # Vérifier si c'est un week-end
        if check_date.weekday() >= 5:  # 5=samedi, 6=dimanche
            continue
        
        # Vérifier si c'est un jour férié
        holidays = MarketHolidays.is_market_holiday(check_date)
        if not holidays:
            return check_date
    
    return None

def is_trading_day(check_date):
    """Vérifie si une date est un jour de trading"""
    if isinstance(check_date, datetime):
        check_date = check_date.date()
    
    # Week-end ?
    if check_date.weekday() >= 5:
        return False
    
    # Jour férié ?
    holidays = MarketHolidays.is_market_holiday(check_date)
    if holidays:
        return False
    
    return True

def get_hardcoded_events():
    """
    Retourne les événements récurrents hardcodés
    Utile pour les événements qui ne sont pas toujours sur TradingEconomics
    """
    events = {}
    
    today = datetime.now(ZoneInfo("UTC"))
    
    # Générer les 7 prochains mercredis pour EIA Crude Oil Inventories
    # Publié chaque mercredi à 10:30 ET (16:30 Paris)
    for i in range(7):
        check_date = today + timedelta(days=i)
        
        # Si c'est un mercredi (weekday=2) et pas un jour férié
        if check_date.weekday() == 2 and is_trading_day(check_date):
            event_datetime = datetime(
                check_date.year, check_date.month, check_date.day,
                10, 30,  # 10:30 AM ET
                tzinfo=ZoneInfo("America/New_York")
            )
            
            event_datetime_paris = event_datetime.astimezone(ZoneInfo("Europe/Paris"))
            
            events[check_date.date().isoformat()] = {
                'name': 'EIA Crude Oil Inventories',
                'time_paris': event_datetime_paris.strftime('%H:%M'),
                'country': '🇺🇸',
                'importance': '⭐⭐⭐⭐',
                'assets': ['CL', 'ES', 'NQ', 'GC', 'BTC', 'ETH'],
                'description': 'US Energy Information Administration - Weekly Petroleum Status Report',
                'datetime': event_datetime_paris
            }
    
    return events
