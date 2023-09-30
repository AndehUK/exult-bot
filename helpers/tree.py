from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands

if TYPE_CHECKING:
    from bot import ExultBot


class Tree(app_commands.CommandTree):
    def __init__(self, client: ExultBot, *, fallback_to_global: bool = True) -> None:
        super().__init__(client=client, fallback_to_global=fallback_to_global)

    async def on_error(
        self, itr: discord.Interaction, error: app_commands.AppCommandError, /
    ) -> None:
        await super().on_error(itr, error)
        return itr.client.dispatch("app_command_error", itr, error)  # Custom bot event
