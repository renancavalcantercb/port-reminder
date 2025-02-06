from datetime import datetime
from db import get_expired_timers, mark_timer_notified


async def check_expired_timers(bot):
    current_time = datetime.utcnow()
    expired_timers = await get_expired_timers(current_time)

    for timer in expired_timers:
        timer_id = timer["id"]
        user_id = timer["user_id"]
        channel_id = timer["channel_id"]
        ship_name = timer["ship_name"]

        channel_id = int(channel_id)
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(f"<@{user_id}>, your timer for {ship_name} has expired!")
        await mark_timer_notified(timer_id)
