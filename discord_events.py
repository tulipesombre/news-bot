import discord
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class DiscordEventManager:
    
    @staticmethod
    async def create_events_for_week(bot, guild_id, events_dict):
        """Crée un Discord Event pour chaque annonce de la semaine"""
        guild = bot.get_guild(guild_id)
        if not guild:
            print(f"❌ Guild {guild_id} introuvable")
            return
        
        existing_events = await guild.fetch_scheduled_events()
        for event in existing_events:
            if any(keyword in event.name.lower() for keyword in ["nfp", "cpi", "fed", "ecb", "oil", "earnings"]):
                try:
                    await event.delete()
                except:
                    pass
        
        created_count = 0
        
        for date_str, event_data in events_dict.items():
            try:
                date_obj = datetime.fromisoformat(date_str)
                time_str = event_data.get("time_paris", "09:00")
                
                if time_str == "Variable":
                    time_str = "09:00"
                
                hour, minute = map(int, time_str.split(":"))
                event_datetime = datetime(
                    date_obj.year, date_obj.month, date_obj.day,
                    hour, minute, tzinfo=ZoneInfo("Europe/Paris")
                )
                
                if event_datetime < datetime.now(ZoneInfo("Europe/Paris")):
                    continue
                
                # Créer l'événement Discord avec les bons attributs
                discord_event = await guild.create_scheduled_event(
                    name=f"{event_data['country']} {event_data['name']}",
                    description=(
                        f"**Importance:** {event_data['importance']}\n"
                        f"**Heure:** {event_data['time_paris']} (Paris)\n"
                        f"**Assets concernés:** {', '.join(event_data['assets'])}\n\n"
                        f"{event_data['description']}"
                    ),
                    start_time=event_datetime,
                    end_time=event_datetime + timedelta(hours=1),
                    location="Calendrier économique",
                    privacy_level=discord.PrivacyLevel.guild_only,
                    entity_type=discord.EntityType.external,
                )
                
                created_count += 1
                print(f"✅ Event créé: {event_data['name']} - {date_str} {time_str}")
            
            except Exception as e:
                print(f"❌ Erreur création event {event_data.get('name', 'Unknown')}: {e}")
        
        print(f"✅ Total: {created_count} Discord Events créés")
        return created_count
