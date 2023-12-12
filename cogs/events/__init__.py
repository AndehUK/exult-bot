from __future__ import annotations

import traceback
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from helpers.cog import Cog
from helpers.colour import Colours
from helpers.embed import Embed

if TYPE_CHECKING:
    from bot import ExultBot
    from helpers.types import ExultInteraction


class BotEvents(Cog):
    async def register_guild(self, guild: discord.Guild) -> None:
        try:
            await self.bot.db.guild.upsert(
                {"guild_id": guild.id}, {"create": {"guild_id": guild.id}, "update": {}}
            )
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
        except Exception as e:
            tb = traceback.format_exc()
            self.bot.logger.error(f"{type(e)} Failed to add guild to db:\n{tb}")

    @Cog.listener("on_guild_join")
    async def on_guild_join(
        self, guild: discord.Guild, *, register_only: bool = False
    ) -> None:
        await self.register_guild(guild)
        # TODO: Add logging for joining a guild

    @Cog.listener("on_app_command_error")
    async def on_app_command_error_log(
        self, itr: ExultInteraction, error: app_commands.AppCommandError
    ) -> None:
        error_msg = (
            "Please ensure you are running this command in a command channel!"
            if isinstance(error, app_commands.CheckFailure)
            else str(error)
        )
        if itr.is_expired():
            func = itr.followup.send
        else:
            func = itr.response.send_message
        try:
            await func(error_msg, ephemeral=True)
        except:
            self.bot.logger.critical(f"[APP_COMMAND_ERROR] {error}")

    @commands.Cog.listener("on_error")
    async def on_error_log(self) -> None:
        embed = Embed(
            title="An Error Occurred!",
            description=traceback.format_exc()[:2048],
            colour=Colours.red,
        )

        channel = self.bot.get_channel(0)
        if not isinstance(channel, discord.TextChannel):
            self.bot.logger.error(
                "on_error event triggered. "
                "Check the logs folder for more information"
            )
            return

        await channel.send(embed=embed)


async def setup(bot: ExultBot) -> None:
    await bot.add_cog(BotEvents(bot))
