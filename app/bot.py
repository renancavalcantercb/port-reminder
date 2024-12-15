import discord
from discord.ext import commands, tasks
from tasks import check_expired_timers
from db import init_db
from commands.reminder import reminder
from dotenv import load_dotenv
from os import getenv

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command(name="reminder")
async def reminder_command(ctx):
    await reminder(ctx, bot)


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
