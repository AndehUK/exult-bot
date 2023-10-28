from __future__ import annotations

# Core Imports
from typing import Any, Dict, TYPE_CHECKING

# Third Party Packages
import discord
from discord import app_commands

# Local Imports
from helpers.colour import Colours
from helpers.embed import Embed
from .builder import MessageBuilder
from .scheduler import MessageScheduler

# Type Imports
if TYPE_CHECKING:
    from bot import ExultBot
    from helpers.types import ExultInteraction


class MessagesCog(MessageBuilder, MessageScheduler):
    """
    Messages Cog - Contains everything regarding:

    - Creating, sending and saving of embedded messages
    - Scheduling of saved messages at a given date/time/interval
    """

    def __init__(self, bot: ExultBot) -> None:
        super().__init__(bot)
        self.ctx_menu_msg_source = app_commands.ContextMenu(
            name="Message Source", callback=self.message_source
        )
        self.bot.tree.add_command(self.ctx_menu_msg_source)

    async def message_source(
        self, itr: ExultInteraction, message: discord.Message
    ) -> None:
        try:
            source_dict: Dict[str, Any] = {
                "content": message.content,
                "embeds": [e.to_dict() for e in message.embeds],
            }

            if len(str(source_dict)) > 2030:
                content_chunks = discord.utils.as_chunks(str(source_dict), 2030)
                content = [f"```json\n{c}\n```" for c in content_chunks]
            else:
                content = f"```json\n{source_dict}\n```"

            if isinstance(content, str):
                embed = Embed(
                    title="Message Source (JSON)",
                    description=content,
                    colour=Colours.gold,
                )
                return await itr.response.send_message(embed=embed, ephemeral=True)
            else:
                embeds = [Embed(title=f"Message Source (JSON)", description=content[0])]
                for cnt in content[1:]:
                    embeds.append(Embed(description=cnt))
                return await itr.response.send_message(embeds=embeds, ephemeral=True)
        except Exception as e:
            await itr.response.send_message(f"{type(e)}: {e}", ephemeral=True)


async def setup(bot: ExultBot) -> None:
    """Loads the extension and all of its commands and listeners to the bot"""
    await bot.add_cog(MessagesCog(bot))
