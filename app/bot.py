import discord
from discord.ext import commands, tasks
from tasks import check_expired_timers
from db import init_db
from commands.reminder import reminder
from commands.active import list_active_timers
from commands.star import list_stars
from dotenv import load_dotenv
from os import getenv

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command(name="reminder")
async def reminder_command(ctx):
    await reminder(ctx, bot)


@bot.command(name="active")
async def list_active_timers_command(ctx):
    await list_active_timers(ctx)


@bot.command(name="stars")
async def list_stars_command(ctx):
    await list_stars(ctx)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    check_timers.start()


@tasks.loop(seconds=60)
async def check_timers():
    await check_expired_timers(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())
    bot.run(getenv("DISCORD_BOT_TOKEN"))
