import discord
from discord.ext import commands, tasks
from tasks import check_expired_timers
from db import init_db
from db import get_registered_users
from utils import get_star_data
from commands.reminder import reminder
from commands.active import list_active_timers
from commands.star import list_stars
from commands.register_star import register_star
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
    notify_stars.start(bot)


@tasks.loop(seconds=60)
async def check_timers():
    await check_expired_timers(bot)


@bot.command(name="register_star")
async def register_star_command(ctx, member: discord.Member = None):
    await register_star(ctx, member)


@tasks.loop(minutes=5)
async def notify_stars(bot):
    channel_id = int(getenv("STAR_CHANNEL_ID"))
    channel = bot.get_channel(channel_id)
    if not channel:
        print("Channel not found")
        return

    df, error = await get_star_data()
    if error:
        print(f"Error fetching star data: {error}")
        return

    if df.empty:
        print("No stars available for notification.")
        return

    upcoming_stars = df[df["Time_remaining"] <= 10]
    if upcoming_stars.empty:
        print("No upcoming stars within 10 minutes.")
        return

    registered_users = await get_registered_users()
    if not registered_users:
        print("No registered users to notify.")
        return

    mentions = [f"<@{user_id}>" for user_id, _ in registered_users]

    notified_stars = set()

    for _, row in upcoming_stars.iterrows():
        star_key = (row["World"], row["Region"], row["Time_remaining"])
        if star_key in notified_stars:
            continue

        try:
            await channel.send(
                f"{', '.join(mentions)}, a star is coming soon!\n"
                f"**Size:** {row['Size']} | **World:** {row['World']} | **Region:** {row['Region']} | "
                f"**Time Remaining:** {row['Time_remaining']} minutes."
            )
            notified_stars.add(star_key)
        except Exception as e:
            print(f"Failed to notify for star {star_key}: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())
    bot.run(getenv("DISCORD_BOT_TOKEN"))
