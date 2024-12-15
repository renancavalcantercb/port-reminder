from datetime import datetime
from db import get_expired_timers, mark_timer_notified


async def check_expired_timers(bot):
    current_time = datetime.utcnow()
    expired_timers = await get_expired_timers(current_time)

    for timer_id, user_id, channel_id, ship_name in expired_timers:
        channel = bot.get_channel(int(channel_id))
        if channel:
            await channel.send(f"<@{user_id}>, your timer for {ship_name} has expired!")
        await mark_timer_notified(timer_id)
