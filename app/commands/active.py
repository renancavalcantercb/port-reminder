from db import get_active_timers
from datetime import datetime
from utils import log_event


async def list_active_timers(ctx):
    user_id = ctx.message.author.id
    user_name = ctx.message.author.name

    log_event(
        "info",
        "Command `list_active_timers` called.",
        user_name=user_name,
        user_id=user_id,
    )
    active_timers = await get_active_timers(user_id)

    if not active_timers:
        await ctx.send("You have no active timers.")
        return

    current_time = datetime.utcnow()

    timers_message = "\n".join(
        f"**{ship_name}** - Ends at: `{timer_end}` - Remaining: `{remaining_minutes} minutes`"
        for ship_name, timer_end in active_timers
        if (
            remaining_minutes := (
                datetime.fromisoformat(timer_end) - current_time
            ).total_seconds()
            // 60
        )
        >= 0
    )

    if timers_message:
        await ctx.send(f"Here are your active timers:\n{timers_message}")
    else:
        await ctx.send("You have no active timers.")
