from discord.ui import Button, View
import discord
from db import (
    add_or_update_curse_counter,
    get_curse_counters,
    undo_last_curse_counter as db_undo_last_curse_counter,
)
from utils import log_event

curse_word_emojis = {
    "😡": "Pedro",
    "🤯": "Ace",
    "🤢": "King",
    "🤮": "Liru",
    "🤐": "Cute",
    "🤬": "Maria Clara",
    "🥶": "Tatá",
}


async def create_buttons(ctx):
    """
    Creates buttons for each user and sends the interactive message.
    """
    view = View()

    for emoji, name in curse_word_emojis.items():
        button = Button(label=name, emoji=emoji, style=discord.ButtonStyle.primary)

        async def button_callback(interaction, emoji=emoji, name=name):
            await interaction.response.defer()

            await add_or_update_curse_counter(emoji, name)
            counters = await get_curse_counters(name)

            updated_count = counters[0].get("count")

            log_event(
                "info",
                f"Button {name} ({emoji}) clicked.",
                user_name=interaction.user.name,
                user_id=interaction.user.id,
            )

            await interaction.followup.send(
                f"{emoji} {name} now has {updated_count} curse words!", ephemeral=False
            )

        button.callback = button_callback
        view.add_item(button)

    undo_button = Button(label="Undo Last", style=discord.ButtonStyle.danger, emoji="↩️")

    async def undo_callback(interaction):
        await interaction.response.defer()
        last_undone = await db_undo_last_curse_counter()

        log_event(
            "info",
            "Button Undo Last clicked.",
            user_name=interaction.user.name,
            user_id=interaction.user.id,
        )

        if last_undone:
            emoji, name, count = last_undone
            await interaction.followup.send(
                f"{emoji} {name} now has {count} curse words!", ephemeral=False
            )
        else:
            await interaction.followup.send(
                "No curse words to undo!", ephemeral=False
            )

    undo_button.callback = undo_callback
    view.add_item(undo_button)

    log_event(
        "info",
        "Command `create_buttons` called.",
        user_name=ctx.message.author.name,
        user_id=ctx.message,
    )

    await ctx.send(
        "👀 Curse Word Tracker! Click a button to add a curse word:", view=view
    )

async def show_rankings(ctx):
    """
    Displays the rankings of curse word counters from the database.
    """
    counters = await get_curse_counters()

    log_event(
        "info",
        "Command `show_rankings` called.",
        user_name=ctx.message.author.name,
        user_id=ctx.message.author.id,
    )

    if not counters:
        await ctx.send("🚨 **No curse word data found!**")
        return

    table = "📊 **Curse Word Rankings** 📊\n"
    table += "```\n"
    table += f"{'🏆':<2} {'Emoji':<6} │ {'Name':<15} │ {'Count':<8}\n"
    table += "—" * 36 + "\n"

    for idx, row in enumerate(sorted(counters, key=lambda x: x["count"], reverse=True), start=1):
        emoji = row.get("emoji")
        name = row.get("name")
        count = row.get("count")
        table += f"{idx:<2} {emoji:<6} │ {name:<15} │ {count:<8}\n"

    table += "```"
    await ctx.send(table)
