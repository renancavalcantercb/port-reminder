from discord import Member
from db import register_user


async def register_star(ctx, member: Member = None):
    target = member or ctx.author
    user_id = str(target.id)
    username = target.name

    message = await register_user(user_id, username)
    await ctx.send(message)
