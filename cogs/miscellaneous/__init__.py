from __future__ import annotations

# Core Imports
from typing import TYPE_CHECKING

# Local Imports
from .emojis import Emojis

# Type Imports
if TYPE_CHECKING:
    from bot import ExultBot


class Miscellaneous(Emojis):
    """
    Miscellaneous Cog - Contains everything regarding:

    - Emoji creation, deletion and stealing
    """


async def setup(bot: ExultBot) -> None:
    """Loads the extension and all of its commands and listeners to the bot"""
    await bot.add_cog(Miscellaneous(bot))
