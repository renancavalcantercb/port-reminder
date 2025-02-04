from utils import create_embed
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
        embed = create_embed(
            title="Upcoming Stars (S10 and S9)",
            description="There are no stars currently available for S10 or S9.",
            color=0xFF0000,
        )
        await ctx.send(embed=embed)
        return

    fields = []
    for _, row in df.iterrows():
        fields.append(
            (
                f"{row['Size']} - {row['Region']}",
                f"**World:** {row['World']} | **Time Remaining:** {row['Time_remaining']} minutes | **Time:** {row['Time']}",
                False,
            )
        )

    embed = create_embed(
        title="Upcoming Stars (S10 and S9)",
        description="Here are the upcoming stars:",
        fields=fields,
    )

    await ctx.send(embed=embed)
