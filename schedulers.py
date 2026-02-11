from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from zoneinfo import ZoneInfo
from discord_events import DiscordEventManager
from scraper import TradingEconomicsScraper
from utils import get_hardcoded_events
import discord

scheduler = AsyncIOScheduler()
scraper = TradingEconomicsScraper()

async def send_weekly_agenda(bot, channel_id, guild_id):
    """Envoie le message de l'agenda + crée les Discord Events"""
    channel = bot.get_channel(channel_id)
    
    print("📅 Début scraping TradingEconomics...")
    
    hardcoded_events = get_hardcoded_events()
    scraped_events = scraper.get_calendar_events(days_ahead=7)
    
    all_events = {**hardcoded_events, **scraped_events}
    
    print(f"📊 Total événements: {len(all_events)}")
    
    await DiscordEventManager.create_events_for_week(bot, guild_id, all_events)
    
    if not all_events:
        await channel.send("❌ Aucun événement économique majeur cette semaine")
        return
    
    embed = discord.Embed(
        title="📅 Agenda Économique - Semaine du " + datetime.now(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y"),
        color=discord.Color.blue(),
        description="Toutes les annonces sont créées en Discord Events ⬇️\n*Clique 'Participer' pour recevoir des notifications*"
    )
    
    sorted_events = sorted(all_events.items(), key=lambda x: x[0])
    
    for date_str, event_data in sorted_events:
        day_name = datetime.fromisoformat(date_str).strftime("%A")
        day_fr = {
            "Monday": "Lundi",
            "Tuesday": "Mardi",
            "Wednesday": "Mercredi",
            "Thursday": "Jeudi",
            "Friday": "Vendredi",
            "Saturday": "Samedi",
            "Sunday": "Dimanche"
        }.get(day_name, day_name)
        
        value = (
            f"⏰ **{event_data['time_paris']}** - {event_data['country']} {event_data['name']}\n"
            f"   {event_data['importance']} | Assets: {', '.join(event_data['assets'])}\n"
        )
        
        embed.add_field(
            name=f"📆 {day_fr} ({date_str})",
            value=value,
            inline=False
        )
    
    embed.set_footer(text="🔔 Rappels quotidiens à 7h pour chaque annonce | Données: TradingEconomics")
    await channel.send(embed=embed)
    print("✅ Message agenda envoyé")

async def send_daily_reminder(bot, channel_id):
    """Envoie le rappel quotidien des annonces du jour"""
    channel = bot.get_channel(channel_id)
    
    hardcoded_events = get_hardcoded_events()
    scraped_events = scraper.get_calendar_events(days_ahead=1)
    all_events = {**hardcoded_events, **scraped_events}
    
    today = datetime.now(ZoneInfo("Europe/Paris")).date().isoformat()
    today_events = {k: v for k, v in all_events.items() if k == today}
    
    if not today_events:
        return
    
    embed = discord.Embed(
        title="🔔 Annonces Économiques Aujourd'hui",
        color=discord.Color.gold(),
        description=datetime.now(ZoneInfo("Europe/Paris")).strftime("%A %d %B %Y")
    )
    
    for date_str, event_data in today_events.items():
        embed.add_field(
            name=f"{event_data['country']} {event_data['name']} - {event_data['time_paris']}",
            value=(
                f"**Importance:** {event_data['importance']}\n"
                f"**Assets:** {', '.join(event_data['assets'])}\n"
                f"{event_data['description']}"
            ),
            inline=False
        )
    
    await channel.send(embed=embed)
    print(f"✅ Rappel quotidien envoyé ({len(today_events)} annonces)")

def start_scheduler(bot, channel_id, guild_id):
    """Démarre le planificateur"""
    
    scheduler.add_job(
        send_weekly_agenda,
        CronTrigger(day_of_week="mon", hour=7, minute=0, timezone="Europe/Paris"),
        args=[bot, channel_id, guild_id],
        id="weekly_agenda"
    )
    
    scheduler.add_job(
        send_daily_reminder,
        CronTrigger(hour=7, minute=0, timezone="Europe/Paris"),
        args=[bot, channel_id],
        id="daily_reminder"
    )
    
    scheduler.start()
    print("✅ Scheduler démarré")
