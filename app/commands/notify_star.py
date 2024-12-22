from db import get_registered_users
from utils import get_star_data
from os import getenv
from utils import log_event
from utils import create_embed


async def notify_stars(bot):
    channel_id = int(getenv("STAR_CHANNEL_ID"))
    channel = bot.get_channel(channel_id)
    if not channel:
        log_event("error", "Channel not found")
        return

    df, error = await get_star_data()
    if error:
        log_event("error", f"Error fetching star data: {error}")
        return

    if df.empty:
        log_event("info", "No stars available for notification.")
        return

    upcoming_stars = df[df["Time_remaining"] <= 10]
    if upcoming_stars.empty:
        log_event("info", "No upcoming stars within 10 minutes.")
        return

    registered_users = await get_registered_users()
    if not registered_users:
        log_event("error", "No registered users to notify.")
        return

    mentions = [f"<@{user_id}>" for user_id, _ in registered_users]

    notified_stars = set()

    for _, row in upcoming_stars.iterrows():
        star_key = (row["World"], row["Region"], row["Time_remaining"])
        if star_key in notified_stars:
            continue

        try:
            message = f"{', '.join(mentions)}, a star is coming soon!"

            fields = [
                (
                    f"{row['Size']} - {row['Region']}",
                    f"**World:** {row['World']} | **Time Remaining:** {row['Time_remaining']} minutes | **Time:** {row['Time']}",
                    False
                )
            ]

            embed = create_embed(
                title="Upcoming Star Notification",
                description="A star is coming soon!",
                fields=fields
            )

            await channel.send(message, embed=embed)
            notified_stars.add(star_key)
        except Exception as e:
            log_event("error", f"Failed to notify for star {star_key}: {e}")
