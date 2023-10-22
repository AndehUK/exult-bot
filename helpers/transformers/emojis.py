from __future__ import annotations

# Core Imports
from typing import List, Optional, TYPE_CHECKING

# Third Party Packages
import discord
from discord import app_commands

# Type Imports
if TYPE_CHECKING:
    from bot import ExultBot

__all__ = ("GuildEmojiTransformer",)


class GuildEmojiTransformer(app_commands.Transformer):
    """
    :class:`discord.app_commands.Transformer` subclass that provides the end-user
    with a selection of all emojis in the current guild, and transforms the given
    value to an instance of :class:`discord.Emoji`.
    """

    async def autocomplete(
        self, itr: discord.Interaction[ExultBot], value: str
    ) -> List[app_commands.Choice[int]]:
        assert itr.guild

        return [
            app_commands.Choice(name=e.name, value=e.id)
            for e in itr.guild.emojis
            if value.lower() in e.name.lower()
        ]

    async def transform(
        self, itr: discord.Interaction[ExultBot], value: int | str
    ) -> Optional[discord.Emoji]:
        assert itr.guild

        if isinstance(value, str):
            return discord.utils.get(itr.guild.emojis, name=value)

        return itr.guild.get_emoji(value)
