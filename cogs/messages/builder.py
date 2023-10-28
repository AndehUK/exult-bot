from __future__ import annotations

# Core Imports
from typing import TYPE_CHECKING

# Third Party Packages
import discord
from discord import app_commands

# Local Imports
from helpers.cog import Cog
from .embeds import MessageManagerEmbed
from .views import MessageManager

# Type Imports
if TYPE_CHECKING:
    from helpers.types import ExultInteraction


class MessageBuilder(Cog):
    """Feature currently undergoing development!!"""

    message = app_commands.Group(
        name="message",
        description="Message Utility Handler!",
        guild_only=True,
        default_permissions=discord.Permissions(manage_guild=True),
    )

    @message.command(
        name="manager", description="Create, edit and delete custom reusable messages!"
    )
    async def message_manager(self, itr: ExultInteraction) -> None:
        view = MessageManager(itr)
        await itr.response.send_message(embed=MessageManagerEmbed, view=view)
