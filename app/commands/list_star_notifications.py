from db import get_registered_users
from utils import create_embed


async def list_star_notifications(ctx):
    registered_users = await get_registered_users()
    if not registered_users:
        embed = create_embed(
            title="Star Notification Users",
            description="No users are registered for star notifications.",
            color=0xFF0000,
        )
        await ctx.send(embed=embed)
        return

    fields = [
        (f"{username} ({user_id})", "Registered for star notifications", False)
        for user_id, username in registered_users
    ]

    embed = create_embed(
        title="Registered Users for Star Notifications",
        description="Here are the users registered for star notifications:",
        fields=fields,
    )

    await ctx.send(embed=embed)
