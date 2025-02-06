from db import get_active_timers
from datetime import datetime
from utils import log_event
from utils import create_embed

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
        embed = create_embed(
            title="Active Timers",
            description="You have no active timers.",
            color=0xFF0000,
        )
        await ctx.send(embed=embed)
        return

    current_time = datetime.utcnow()

    timers_message = ""
    for ship_name, timer_end in active_timers:
        if timer_end:
            try:
                timer_end_dt = datetime.strptime(timer_end, "%Y-%m-%d %H:%M:%S")
                remaining_minutes = (timer_end_dt - current_time).total_seconds() // 60

                if remaining_minutes >= 0:
                    timers_message += f"**{ship_name}** - Ends at: `{timer_end}` - Remaining: `{remaining_minutes} minutes`\n"
            except ValueError:
                print(f"Erro ao converter timer_end: {timer_end}")

    if timers_message:
        embed = create_embed(
            title="Active Timers",
            description="Here are your active timers:",
            fields=[("Timers", timers_message, False)],
        )
        await ctx.send(embed=embed)
    else:
        embed = create_embed(
            title="Active Timers",
            description="You have no active timers.",
            color=0xFF0000,
        )
        await ctx.send(embed=embed)
