from db import delete_user
from utils import create_embed


async def remove_star_notification(ctx, member):
    target = member or ctx.author
    user_id = str(target.id)
    username = target.name

    try:
        response = await delete_user(user_id)

        if response:
            embed = create_embed(
                title="Star Notification Removal",
                description=f"Successfully removed user {username} from star notifications!",
                color=0x1F8B4C,
            )
            await ctx.send(embed=embed)
            return
    except Exception as e:
        embed = create_embed(
            title="Star Notification Removal",
            description=f"Failed to remove user {username} from star notifications!",
            color=0xFF0000,
        )
        await ctx.send(embed=embed)
        return
