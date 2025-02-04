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
}


async def create_buttons(ctx):
    """
    Creates buttons for each user and sends the interactive message.
    """
    view = View()

    for emoji, name in curse_word_emojis.items():
        button = Button(label=name, emoji=emoji, style=discord.ButtonStyle.primary)

        async def button_callback(interaction, emoji=emoji, name=name):
            await add_or_update_curse_counter(emoji, name)
            counters = await get_curse_counters()
            updated_count = next((row[2] for row in counters if row[0] == emoji), 0)

            log_event(
                "info",
                f"Button {name} ({emoji}) clicked.",
                user_name=interaction.user.name,
                user_id=interaction.user.id,
            )

            await interaction.response.send_message(
                f"{name} now has {updated_count} curse words!", ephemeral=False
            )

        button.callback = button_callback
        view.add_item(button)

    undo_button = Button(label="Undo Last", style=discord.ButtonStyle.danger, emoji="↩️")

    async def undo_callback(interaction):
        last_undone = await db_undo_last_curse_counter()

        log_event(
            "info",
            "Button Undo Last clicked.",
            user_name=interaction.user.name,
            user_id=interaction.user.id,
        )

        if last_undone:
            emoji, name = last_undone
            await interaction.response.send_message(
                f"Undid the last curse word for {name} ({emoji}).", ephemeral=False
            )
        else:
            await interaction.response.send_message(
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
        await ctx.send("No curse word data found!")
        return

    table = "📊 **Curse Word Rankings**\n"
    table += "```\n"
    table += f"{'Emoji':<6} {'Name':<15} {'Count':<10}\n"
    table += "-" * 35 + "\n"

    for emoji, name, count in counters:
        table += f"{emoji:<6} {name:<15} {count:<10}\n"

    table += "```"
    await ctx.send(table)
