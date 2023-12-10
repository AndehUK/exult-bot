from __future__ import annotations

# Core Imports
from typing import Optional, TYPE_CHECKING

# Third Party Packages
import discord

# Type Imports
if TYPE_CHECKING:
    from bot import ExultBot
    from .types import ExultInteraction


# Image types that we accept that our `is_image_valid` coroutine checks against
VALID_IMAGE_CONTENT_TYPES = (
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/gif",
    "image/webp",
)


async def is_image_valid(bot: ExultBot, url: str) -> bool:
    """
    Checks to see if the provided URL is a valid direct image URL
    """

    try:
        # Performs a HTTP head request to the given URL
        async with bot.session.head(url) as r:
            content = r.headers.get("content-type")
            return content in VALID_IMAGE_CONTENT_TYPES
    except:
        pass
    return False


async def check_role_permissions(
    guild: discord.Guild,
    role: discord.Role,
    *,
    itr: Optional[ExultInteraction] = None,
    target: Optional[discord.Member] = None,
) -> bool:
    if itr:
        assert isinstance(itr.user, discord.Member)

    if not guild.me.guild_permissions.manage_roles:
        if itr is not None:
            await itr.response.send_message(
                "I don't have the required permissions to manage roles!",
                ephemeral=True,
            )
        return False
    if role > guild.me.top_role:
        if itr is not None:
            await itr.response.send_message(
                "I cannot manage roles higher than my own!", ephemeral=True
            )
        return False
    if target:
        if role > target.top_role:
            if itr is not None:
                await itr.response.send_message(
                    "You cannot manage roles higher than your own!", ephemeral=True
                )
            return False

    return True
