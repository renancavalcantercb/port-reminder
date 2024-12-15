import re
from datetime import datetime, timedelta
from discord.ext import commands
import discord
from db import add_timer


async def reminder(ctx, bot):
    ship_options = [
        discord.SelectOption(label="Ship 1", value="Ship 1"),
        discord.SelectOption(label="Ship 2", value="Ship 2"),
        discord.SelectOption(label="Ship 3", value="Ship 3"),
        discord.SelectOption(label="Ship 4", value="Ship 4"),
    ]

    select = discord.ui.Select(placeholder="Choose a ship", options=ship_options)

    async def select_callback(interaction):
        ship_name = select.values[0]

        await interaction.response.send_message(
            f"You chose {ship_name}. Please enter the time in the format `00h 00m`."
        )

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            user_msg = await bot.wait_for("message", check=check, timeout=60)
            time_input = user_msg.content.strip()

            time_match = re.match(r"(\d{1,2})h\s*(\d{1,2})m", time_input)

            if time_match:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                total_minutes = hours * 60 + minutes
                timer_end = datetime.utcnow() + timedelta(minutes=total_minutes)

                await add_timer(
                    interaction.user.id, interaction.channel.id, ship_name, timer_end
                )

                await interaction.followup.send(
                    f"Reminder set for {ship_name} in {hours} hours and {minutes} minutes."
                )
            else:
                await interaction.followup.send(
                    "Invalid time format. Please use the format `00h 00m`."
                )
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "You took too long to respond. Please try again."
            )

    select.callback = select_callback
    view = discord.ui.View()
    view.add_item(select)

    await ctx.send("Choose a ship for the reminder:", view=view)
