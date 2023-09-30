from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

from .logger import Logger

if TYPE_CHECKING:
    from bot import ExultBot


class Cog(commands.Cog):
    bot: ExultBot
    logger: Logger

    def __init__(self, bot: ExultBot) -> None:
        self.bot = bot
        self.logger = Logger(f"cogs/{self.__class__.__name__.lower()}")
