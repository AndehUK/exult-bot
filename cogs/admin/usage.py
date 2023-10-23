from __future__ import annotations

# Core Imports
from typing import Any, Optional, TYPE_CHECKING

# Third Party Packages
from discord import app_commands
from prisma.enums import UsageMode

# Local Imports
from helpers.cog import Cog
from helpers.embed import Embed
from helpers.transformers import UsageModeTransformer

# Type Imports
if TYPE_CHECKING:
    from helpers.types import ExultInteraction


class Usage(Cog):
    """Contains usage-related commands and listeners"""

    usage = app_commands.Group(
        name="usage",
        description="Configure how you allow us to track usage!",
        guild_only=False,
    )

    @Cog.listener("on_app_command_completion")
    async def on_app_command_completion(
        self,
        itr: ExultInteraction,
        command: app_commands.Command[Any, ..., Any],
    ) -> None:
        await itr.client.db.usage.upsert(
            where={
                "command_name_invoker_id": {
                    "command_name": command.qualified_name,
                    "invoker_id": itr.user.id,
                }
            },
            data={
                "create": {
                    "command_name": command.qualified_name,
                    "invoker_id": itr.user.id,
                    "uses": 1,
                },
                "update": {"uses": {"increment": 1}},
            },
        )

    @usage.command(
        name="mode",
        description="Tell us how you would like us to track your command usage, if at all.",
    )
    async def usage_mode(
        self,
        itr: ExultInteraction,
        mode: app_commands.Transform[Optional[UsageMode], UsageModeTransformer],
    ) -> None:
        await itr.response.defer(ephemeral=True)

        if not mode:
            return

        content = f"We have updated your tacking settings to `{mode.value.title().replace('_', ' ')}`!"
        embed = Embed(
            title="Why do we track command usage?",
            description=(
                "Tracking command usage helps my developers get a deeper "
                "understanding of what commands are popular, in what server "
                "and by which people! We only use this data to improve the User "
                "Experience of our features and nothing else, you can view our "
                "Terms of Service and Privacy Policy using the buttons below!"
            ),
            thumbnail=itr.client.user.display_avatar.url,
        )
        await itr.followup.send(content=content, embed=embed, ephemeral=True)
