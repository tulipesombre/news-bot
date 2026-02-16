from datetime import datetime, date
from zoneinfo import ZoneInfo

class MarketHolidays:
    """Gestion des jours fériés des marchés US et UK"""
    
    @staticmethod
    def get_us_holidays(year):
        """Retourne les jours fériés US (NYSE fermée)"""
        holidays = {
            # Jours fixes
            date(year, 1, 1): "New Year's Day 🇺🇸",
            date(year, 7, 4): "Independence Day 🇺🇸",
            date(year, 12, 25): "Christmas Day 🇺🇸",
            
            # MLK Day - 3ème lundi de janvier
            MarketHolidays._get_nth_weekday(year, 1, 0, 3): "Martin Luther King Jr. Day 🇺🇸",
            
            # Presidents Day - 3ème lundi de février
            MarketHolidays._get_nth_weekday(year, 2, 0, 3): "Presidents' Day 🇺🇸",
            
            # Memorial Day - dernier lundi de mai
            MarketHolidays._get_last_weekday(year, 5, 0): "Memorial Day 🇺🇸",
            
            # Labor Day - 1er lundi de septembre
            MarketHolidays._get_nth_weekday(year, 9, 0, 1): "Labor Day 🇺🇸",
            
            # Thanksgiving - 4ème jeudi de novembre
            MarketHolidays._get_nth_weekday(year, 11, 3, 4): "Thanksgiving Day 🇺🇸",
        }
        
        # Good Friday (Pâques - 2 jours)
        easter = MarketHolidays._get_easter(year)
        good_friday = date(easter.year, easter.month, easter.day - 2) if easter.day > 2 else date(easter.year, easter.month - 1, easter.day + 28)
        holidays[good_friday] = "Good Friday 🇺🇸"
        
        return holidays
    
    @staticmethod
    def get_uk_holidays(year):
        """Retourne les jours fériés UK (LSE fermée)"""
        holidays = {
            # Jours fixes
            date(year, 1, 1): "New Year's Day 🇬🇧",
            date(year, 12, 25): "Christmas Day 🇬🇧",
            date(year, 12, 26): "Boxing Day 🇬🇧",
        }
        
        # Easter
        easter = MarketHolidays._get_easter(year)
        good_friday = date(easter.year, easter.month, easter.day - 2) if easter.day > 2 else date(easter.year, easter.month - 1, easter.day + 28)
        easter_monday = date(easter.year, easter.month, easter.day + 1)
        
        holidays[good_friday] = "Good Friday 🇬🇧"
        holidays[easter_monday] = "Easter Monday 🇬🇧"
        
        # Early May Bank Holiday - 1er lundi de mai
        holidays[MarketHolidays._get_nth_weekday(year, 5, 0, 1)] = "Early May Bank Holiday 🇬🇧"
        
        # Spring Bank Holiday - dernier lundi de mai
        holidays[MarketHolidays._get_last_weekday(year, 5, 0)] = "Spring Bank Holiday 🇬🇧"
        
        # Summer Bank Holiday - dernier lundi d'août
        holidays[MarketHolidays._get_last_weekday(year, 8, 0)] = "Summer Bank Holiday 🇬🇧"
        
        return holidays
    
    @staticmethod
    def is_market_holiday(check_date):
        """Vérifie si une date est un jour férié US ou UK"""
        if isinstance(check_date, datetime):
            check_date = check_date.date()
        
        year = check_date.year
        us_holidays = MarketHolidays.get_us_holidays(year)
        uk_holidays = MarketHolidays.get_uk_holidays(year)
        
        holidays_info = []
        
        if check_date in us_holidays:
            holidays_info.append(us_holidays[check_date])
        
        if check_date in uk_holidays:
            holidays_info.append(uk_holidays[check_date])
        
        return holidays_info
    
    @staticmethod
    def _get_nth_weekday(year, month, weekday, n):
        """Retourne le n-ième jour de la semaine d'un mois
        weekday: 0=Lundi, 1=Mardi, ..., 6=Dimanche
        n: 1=premier, 2=deuxième, etc.
        """
        first_day = date(year, month, 1)
        first_weekday = first_day.weekday()
        
        # Calculer le premier jour de ce type dans le mois
        days_until_weekday = (weekday - first_weekday) % 7
        first_occurrence = 1 + days_until_weekday
        
        # Ajouter (n-1) semaines
        target_day = first_occurrence + (n - 1) * 7
        
        return date(year, month, target_day)
    
    @staticmethod
    def _get_last_weekday(year, month, weekday):
        """Retourne le dernier jour de la semaine d'un mois"""
        # Commencer par le dernier jour du mois
        if month == 12:
            last_day = date(year + 1, 1, 1)
        else:
            last_day = date(year, month + 1, 1)
        
        last_day = date(last_day.year, last_day.month, last_day.day - 1)
        
        # Reculer jusqu'au bon jour de la semaine
        while last_day.weekday() != weekday:
            last_day = date(last_day.year, last_day.month, last_day.day - 1)
        
        return last_day
    
    @staticmethod
    def _get_easter(year):
        """Calcul de la date de Pâques (algorithme de Meeus)"""
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        
        return date(year, month, day)
    
    @staticmethod
    def get_upcoming_holidays(days_ahead=30):
        """Retourne les jours fériés à venir"""
        today = datetime.now(ZoneInfo("UTC")).date()
        year = today.year
        
        us_holidays = MarketHolidays.get_us_holidays(year)
        uk_holidays = MarketHolidays.get_uk_holidays(year)
        
        # Si on est en fin d'année, inclure aussi l'année suivante
        if today.month >= 11:
            us_holidays.update(MarketHolidays.get_us_holidays(year + 1))
            uk_holidays.update(MarketHolidays.get_uk_holidays(year + 1))
        
        upcoming = []
        
        for i in range(days_ahead):
            check_date = date(today.year, today.month, today.day)
            from datetime import timedelta
            check_date = today + timedelta(days=i)
            
            holidays = MarketHolidays.is_market_holiday(check_date)
            if holidays:
                upcoming.append({
                    'date': check_date,
                    'holidays': holidays
                })
        
        return upcoming
