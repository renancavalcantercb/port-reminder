from db import delete_user
from utils import create_embed

async def remove_star_notification(ctx, member):
    target = member or ctx.author
    user_id = str(target.id)
    try:
        response = await delete_user(user_id)

        embed = create_embed(
            title="Star Notification Removal",
            description=f"Successfully removed user {ctx.author.name} ({user_id}) from star notifications.",
            color=0x1F8B4C
        )
        await ctx.send(embed=embed)

    except Exception as e:
        embed = create_embed(
            title="Error",
            description=f"An error occurred: {str(e)}",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
