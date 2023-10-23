from __future__ import annotations

# Core Imports
from typing import List, Optional, TYPE_CHECKING

# Third Party Packages
import discord
from discord import app_commands
from prisma.enums import UsageMode

# Type Imports
if TYPE_CHECKING:
    from bot import ExultBot

__all__ = ("UsageModeTransformer",)


class UsageModeTransformer(app_commands.Transformer):
    """
    :class:`discord.app_commands.Transformer` subclass that wraps around
    our :enum:`prisma.enums.UsageMode` enum.
    """

    def format_name(self, mode: UsageMode) -> str:
        return mode.value.lower().replace("_", " ")

    async def autocomplete(
        self, itr: discord.Interaction[ExultBot], value: str
    ) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(
                name=mode.value.title().replace("_", " "), value=mode.value
            )
            for mode in UsageMode
        ]

    async def transform(
        self, itr: discord.Interaction[ExultBot], value: str
    ) -> Optional[UsageMode]:
        try:
            result = UsageMode[value]
            return result
        except:
            return await itr.response.send_message(
                (
                    f"Sorry! `{value}` is not a valid usage tracking mode. "
                    "Please use the autocomplete menu when running this command!"
                ),
                ephemeral=True,
            )
