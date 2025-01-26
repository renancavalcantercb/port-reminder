import discord
import asyncio
from discord.ext import commands, tasks
from tasks import check_expired_timers
from db import init_db
from commands.reminder import reminder
from commands.active import list_active_timers
from commands.star import list_stars
from commands.register_star_notification import register_star_notification
from commands.list_star_notifications import list_star_notifications
from commands.remove_star_notification import remove_star_notification
from commands.notify_star import notify_stars
from commands.curse_word import create_buttons, show_rankings
from dotenv import load_dotenv
from os import getenv
from utils import log_event

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    log_event("info", f"Logged in as {bot.user.name}")
    check_timers.start()


#   check_stars.start(bot)


@bot.command(name="reminder")
async def reminder_command(ctx):
    await reminder(ctx, bot)


@bot.command(name="active")
async def list_active_timers_command(ctx):
    await list_active_timers(ctx)


@tasks.loop(seconds=60)
async def check_timers():
    await check_expired_timers(bot)


@bot.command(name="stars", aliases=["s", "star"])
async def list_stars_command(ctx):
    await list_stars(ctx)


@bot.command(name="register_notify")
async def register_star_command(ctx, member: discord.Member = None):
    await register_star_notification(ctx, member)


@bot.command(name="list_notify")
async def list_notify_command(ctx):
    await list_star_notifications(ctx)


@bot.command(name="remove_notify")
async def remove_notify_command(ctx, member: discord.Member = None):
    await remove_star_notification(ctx, member)


@bot.command("curse_word")
async def curse_word_command(ctx):
    await create_buttons(ctx)


@bot.command("ranking")
async def curse_word_ranking(ctx):
    await show_rankings(ctx)


# @tasks.loop(minutes=5)
async def check_stars(bot):
    await notify_stars(bot)


if __name__ == "__main__":
    asyncio.run(init_db())
    bot.run(getenv("DISCORD_BOT_TOKEN"))
