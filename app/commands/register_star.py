from discord import Member
from db import register_user
from utils import log_event


async def register_star(ctx, member: Member = None):
    target = member or ctx.author
    user_id = str(target.id)
    username = target.name
    author_name = ctx.author.name
    author_id = ctx.author.id

    log_event(
        "info",
        "Command `register_star` called.",
        author_name=author_name,
        author_id=author_id,
        target_username=username,
        target_user_id=user_id,
    )

    message = await register_user(user_id, username)
    await ctx.send(message)
