from discord import Embed
from utils import get_star_data
from utils import log_event


async def list_stars(ctx):
    user_id = ctx.message.author.id
    user_name = ctx.message.author.name

    log_event(
        "info", "Command `list_stars` called.", user_name=user_name, user_id=user_id
    )

    df, error = await get_star_data()
    if error:
        await ctx.send(error)
        return

    if df.empty:
        await ctx.send("No available stars of S10 or S9.")
        return

    embed = Embed(title="Upcoming Stars (S10 and S9)", color=0x1F8B4C)
    for _, row in df.iterrows():
        embed.add_field(
            name=f"{row['Size']} - {row['Region']}",
            value=(
                f"**World:** {row['World']} | "
                f"**Time Remaining:** {row['Time_remaining']} minutes | "
                f"**Time:** {row['Time']}"
            ),
            inline=False,
        )

    footer = "Made by @CuTGuArDiAn"
    embed.set_footer(text=footer)

    await ctx.send(embed=embed)
