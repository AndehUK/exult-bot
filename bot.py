from __future__ import annotations

import traceback
from typing import Optional, Tuple

import aiohttp
import discord
from discord.ext import commands
from prisma import Prisma

from cogs import COGS
from helpers.ipc.routes import ExultBotIPC
from helpers.logger import Logger
from helpers.regex import RegEx
from helpers.tree import Tree


class ExultBot(commands.Bot):
    _is_ready: bool
    db: Prisma
    guilds_to_sync: Tuple[int, ...]
    ipc: ExultBotIPC
    logger: Logger
    regex: RegEx
    session: aiohttp.ClientSession
    sync_on_ready: bool

    def __init__(
        self, *, sync_on_ready: bool = False, guilds_to_sync: Tuple[int, ...] = ()
    ) -> None:
        self._is_ready = False
        self.guilds_to_sync = guilds_to_sync
        self.logger = Logger("ExultBot", console=True)
        self.regex = RegEx()
        self.sync_on_ready = sync_on_ready

        super().__init__(
            command_prefix="e!",
            description="An all-in-one feature rich bot that has moderation, utility and more!",
            intents=discord.Intents.all(),  # All until we know exactly what intents we need
            tree_cls=Tree,
        )

        self.owner_ids = {
            957437570546012240,  # ExHiraku
            268815279570681857,  # lukewain
        }

    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")
        loaded_cogs = 1

        for cog in COGS:
            cog: str
            try:
                await self.load_extension(cog)
                loaded_cogs += 1
            except Exception as e:
                tb = traceback.format_exc()
                self.logger.error(f"{type(e)} Exception in loading {cog}\n{tb}")
                continue

        self.logger.info(f"Successfully loaded {loaded_cogs}/{len(COGS)+1} cogs!")

    async def on_ready(self) -> None:
        if self._is_ready:
            return self.logger.critical("Bot reconnected to Discord Gateway.")
        if self.sync_on_ready and len(self.guilds_to_sync):
            if -1 in self.guilds_to_sync:
                try:
                    global_synced = await self.tree.sync()
                    self.logger.info(f"Synced {len(global_synced)} global commands!")
                except:
                    tb = traceback.format_exc()
                    self.logger.critical(
                        f"Failed to sync global application commands!\n{tb}"
                    )
            for guild_id in [g for g in self.guilds_to_sync if g != -1]:
                try:
                    guild_synced = await self.tree.sync(
                        guild=discord.Object(guild_id, type=discord.Guild)
                    )
                    self.logger.info(
                        f"Synced {len(guild_synced)} commands for guild ({guild_id})"
                    )
                except:
                    tb = traceback.format_exc()
                    self.logger.critical(
                        f"Failed to sync commands for guild ({guild_id})\n{tb}"
                    )
        self._is_ready = True
        self.logger.info(f"{self.user} is now online!")

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        self.logger.info("Starting Bot...")
        async with aiohttp.ClientSession() as self.session, Prisma() as self.db, ExultBotIPC(
            self
        ) as self.ipc:
            try:
                await super().start(token, reconnect=reconnect)
            finally:
                self.logger.info("Shutdown Bot.")

    def get_partial_emoji_with_state(
        self, name: str, animated: bool = False, id: Optional[int] = None
    ) -> discord.PartialEmoji:
        return discord.PartialEmoji.with_state(
            self._connection, name=name, animated=animated, id=id
        )

    async def get_or_fetch_user(self, user_id: int) -> Optional[discord.User]:
        try:
            return self.get_user(user_id) or await self.fetch_user(user_id)
        except discord.HTTPException:
            return None
