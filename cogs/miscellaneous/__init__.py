from __future__ import annotations

from typing import TYPE_CHECKING

from .emojis import Emojis

if TYPE_CHECKING:
    from bot import ExultBot


class Miscellaneous(Emojis):
    """Miscellaneous Cog"""


async def setup(bot: ExultBot) -> None:
    await bot.add_cog(Miscellaneous(bot))
