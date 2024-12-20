from db import get_active_timers
import discord
from datetime import datetime


async def list_active_timers(ctx):
    user_id = ctx.message.author.id

    # Recupera timers ativos do banco usando apenas o user_id
    active_timers = await get_active_timers(user_id)

    # Verifica se há timers ativos
    if not active_timers:
        await ctx.send("You have no active timers.")
        return

    # Obtém o horário atual
    current_time = datetime.utcnow()

    # Formata a mensagem com os timers ativos
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

    # Envia a lista de timers
    if timers_message:
        await ctx.send(f"Here are your active timers:\n{timers_message}")
    else:
        await ctx.send("You have no active timers.")
