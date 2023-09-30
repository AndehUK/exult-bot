from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

import discord
from discord import app_commands


if TYPE_CHECKING:
    from bot import ExultBot


class GuildEmojiTransformer(app_commands.Transformer):
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
