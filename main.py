import discord
from discord.ext import commands
from config import DISCORD_TOKEN, CHANNEL_ID, GUILD_ID
from schedulers import start_scheduler

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté: {bot.user}")
    start_scheduler(bot, CHANNEL_ID, GUILD_ID)
    print("🚀 Bot opérationnel")

@bot.command()
async def agenda(ctx):
    """Commande manuelle pour forcer l'envoi de l'agenda"""
    from schedulers import send_weekly_agenda
    await send_weekly_agenda(bot, ctx.channel.id, GUILD_ID)

@bot.command()
async def test(ctx):
    """Test de connexion"""
    await ctx.send("✅ Bot fonctionnel!")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
