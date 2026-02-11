import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class TradingEconomicsScraper:
    BASE_URL = "https://tradingeconomics.com/calendar"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_calendar_events(self, days_ahead=7):
        """Scrape le calendrier économique de TradingEconomics"""
        try:
            today = datetime.now(ZoneInfo("UTC"))
            end_date = today + timedelta(days=days_ahead)
            
            params = {
                'd1': today.strftime('%Y-%m-%d'),
                'd2': end_date.strftime('%Y-%m-%d')
            }
            
            response = requests.get(self.BASE_URL, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._parse_calendar(soup)
        
        except Exception as e:
            print(f"❌ Erreur scraping TradingEconomics: {e}")
            return {}
    
    def _parse_calendar(self, soup):
        """Parse le HTML du calendrier"""
        events = {}
        
        calendar_table = soup.find('table', {'id': 'calendar'})
        
        if not calendar_table:
            print("⚠️ Table calendrier introuvable")
            return events
        
        rows = calendar_table.find('tbody').find_all('tr')
        current_date = None
        
        for row in rows:
            if 'date' in row.get('class', []):
                date_cell = row.find('td')
                if date_cell:
                    date_text = date_cell.get_text(strip=True)
                    current_date = self._parse_date(date_text)
                continue
            
            if current_date and 'calendar-row' in row.get('class', []):
                event = self._parse_event_row(row, current_date)
                if event:
                    date_key = event['datetime'].date().isoformat()
                    
                    if date_key not in events or event['importance'] == "⭐⭐⭐⭐⭐":
                        events[date_key] = event
        
        return events
    
    def _parse_event_row(self, row, event_date):
        """Parse une ligne d'événement"""
        try:
            cells = row.find_all('td')
            
            if len(cells) < 6:
                return None
            
            time_cell = cells[0]
            country_cell = cells[1]
            event_cell = cells[2]
            importance_cell = cells[3]
            
            time_str = time_cell.get_text(strip=True)
            if not time_str or time_str == 'Tentative' or time_str == 'All Day':
                time_str = '09:00'
            
            event_name = event_cell.get_text(strip=True)
            
            importance_class = importance_cell.get('class', [])
            importance_level = 1
            for cls in importance_class:
                if 'calendar-importance-3' in cls:
                    importance_level = 3
                elif 'calendar-importance-2' in cls:
                    importance_level = 2
            
            if importance_level < 2:
                return None
            
            if not self._is_relevant_event(event_name):
                return None
            
            hour, minute = self._parse_time(time_str)
            event_datetime = datetime(
                event_date.year, event_date.month, event_date.day,
                hour, minute, tzinfo=ZoneInfo("America/New_York")
            )
            
            event_datetime_paris = event_datetime.astimezone(ZoneInfo("Europe/Paris"))
            
            importance_stars = {
                3: "⭐⭐⭐⭐⭐",
                2: "⭐⭐⭐⭐",
                1: "⭐⭐⭐"
            }[importance_level]
            
            country_text = country_cell.get_text(strip=True)
            country_flag = self._get_country_flag(country_text)
            
            simplified_name = self._simplify_event_name(event_name)
            assets = self._get_affected_assets(event_name)
            
            return {
                'name': simplified_name,
                'time_paris': event_datetime_paris.strftime('%H:%M'),
                'country': country_flag,
                'importance': importance_stars,
                'assets': assets,
                'description': event_name,
                'datetime': event_datetime_paris
            }
        
        except Exception as e:
            print(f"⚠️ Erreur parsing row: {e}")
            return None
    
    def _parse_date(self, date_text):
        """Parse le texte de date"""
        try:
            if ',' in date_text:
                parts = date_text.split(',', 1)
                date_text = parts[1].strip()
            
            return datetime.strptime(date_text, '%B %d, %Y')
        except:
            return datetime.now(ZoneInfo("UTC"))
    
    def _parse_time(self, time_str):
        """Parse l'heure"""
        try:
            time_str = time_str.strip()
            
            if 'AM' in time_str or 'PM' in time_str:
                time_obj = datetime.strptime(time_str, '%I:%M %p')
                return time_obj.hour, time_obj.minute
            
            if ':' in time_str:
                parts = time_str.split(':')
                return int(parts[0]), int(parts[1])
            
            return 9, 0
        
        except:
            return 9, 0
    
    def _is_relevant_event(self, event_name):
    """Vérifie si l'événement est pertinent"""
    relevant_keywords = [
        'interest rate', 'fomc', 'fed funds', 'federal reserve',
        'cpi', 'consumer price', 'inflation',
        'ecb', 'european central bank',
        'gdp', 'gross domestic',
        'non farm', 'payroll', 'nfp'  
    ]
    
    event_lower = event_name.lower()
    return any(keyword in event_lower for keyword in relevant_keywords)
    
    def _simplify_event_name(self, name):
        """Simplifie le nom de l'événement"""
        name_lower = name.lower()
        
        if 'interest rate' in name_lower or 'fed funds' in name_lower or 'fomc' in name_lower:
            return "Fed Decision - Taux directeurs"
        elif 'cpi' in name_lower or 'consumer price' in name_lower:
            return "CPI - Inflation USA"
        elif 'ecb' in name_lower:
            return "ECB Decision - Taux BCE"
        elif 'gdp' in name_lower:
            return "GDP - Croissance USA"
        
        return name
    
    def _get_country_flag(self, country_text):
        """Retourne le drapeau selon le pays"""
        country_lower = country_text.lower()
        
        if 'united states' in country_lower or 'usa' in country_lower:
            return "🇺🇸"
        elif 'euro' in country_lower or 'europe' in country_lower:
            return "🇪🇺"
        elif 'united kingdom' in country_lower or 'uk' in country_lower:
            return "🇬🇧"
        elif 'japan' in country_lower:
            return "🇯🇵"
        
        return "🌍"
    
    def _get_affected_assets(self, event_name):
        """Détermine les assets affectés"""
        name_lower = event_name.lower()
        
        if 'fed' in name_lower or 'fomc' in name_lower or 'interest rate' in name_lower:
            return ["ES", "NQ", "GC", "6E", "CL", "BTC", "ETH"]
        elif 'cpi' in name_lower or 'inflation' in name_lower:
            return ["ES", "NQ", "GC", "6E", "BTC", "ETH"]
        elif 'ecb' in name_lower:
            return ["6E", "ES", "NQ", "GC"]
        elif 'gdp' in name_lower:
            return ["ES", "NQ", "6E"]
        
        return ["ES", "NQ"]
