from __future__ import annotations

# Core Imports
from typing import TYPE_CHECKING

# Local Imports
from .usage import Usage

# Type Imports
if TYPE_CHECKING:
    from bot import ExultBot


class AdminCog(Usage):
    """
    Admin Cog - Contains everything regarding:

    - Usage Tracking and Usage mode commands
    """


async def setup(bot: ExultBot) -> None:
    """Loads the extension and all of its commands and listeners to the bot"""
    await bot.add_cog(AdminCog(bot))
