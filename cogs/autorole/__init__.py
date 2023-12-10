from __future__ import annotations

# Core Imports
from typing import List, TYPE_CHECKING

# Third Party Packages
import discord
from discord import app_commands
from prisma.enums import AutoroleMode
from prisma.models import Guild

# Local Imports
from helpers.cog import Cog

# Type Imports
if TYPE_CHECKING:
    from bot import ExultBot
    from helpers.types import ExultInteraction


class AutorolesCog(Cog):
    """
    Autoroles Cog - Contains everything regarding:

    - Configuring autoroles
    - Assigning autoroles
    """

    def __init__(self, bot: ExultBot) -> None:
        super().__init__(bot)

    autoroles_group = app_commands.Group(
        name="autoroles",
        description="Commands to configure autoroles",
        guild_only=True,
        default_permissions=discord.Permissions(manage_guild=True),
    )

    async def get_config(self, guild: discord.Guild) -> Guild:
        config = await self.bot.db.guild.find_unique(
            {"guild_id": guild.id},
            {"autorole_config": {"include": {"autoroles": True}}},
        )
        if not config:
            config = await self.bot.db.guild.create({"guild_id": guild.id})
            await self.bot.db.user.create_many(
                [{"user_id": m.id} for m in guild.members if not m.bot],
                skip_duplicates=True,
            )
            await self.bot.db.member.create_many(
                [
                    {"guild_id": guild.id, "member_id": m.id}
                    for m in guild.members
                    if not m.bot
                ],
                skip_duplicates=True,
            )
        return config

    async def assign_autoroles(self, config: Guild, member: discord.Member) -> None:
        if not member.guild.me.guild_permissions.manage_roles:
            return

        assert config.autorole_config and config.autorole_config.autoroles

        roles: List[discord.Role] = []
        for ar in config.autorole_config.autoroles:
            role = member.guild.get_role(ar.role_id)
            if role and member.guild.me.top_role > role:
                roles.append(role)

        if bool(roles):
            try:
                await member.add_roles(*roles)
            except Exception as e:
                self.logger.critical(
                    f"Failed to assign autoroles to {member} in guild {member.guild.name} ({member.guild.id})! ~ {type(e): {e}}"
                )

    @autoroles_group.command(name="config", description="Configure autoroles!")
    async def autoroles_config(self, itr: ExultInteraction) -> None:
        return

    @Cog.listener("on_member_join")
    async def assign_autoroles_on_join(self, member: discord.Member) -> None:
        config = await self.get_config(member.guild)

        if (
            not config.autorole_config
            or config.autorole_config.autorole_mode != AutoroleMode.on_join
            or not config.autorole_config.autoroles
        ):
            return

        await self.assign_autoroles(config, member)

    @Cog.listener("on_member_update")
    async def assign_autoroles_on_verify(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        if before.pending and not after.pending:
            config = await self.get_config(after.guild)

            if (
                not config.autorole_config
                or config.autorole_config.autorole_mode != AutoroleMode.on_verify
                or not config.autorole_config.autoroles
            ):
                return

            await self.assign_autoroles(config, after)


async def setup(bot: ExultBot) -> None:
    await bot.add_cog(AutorolesCog(bot))
