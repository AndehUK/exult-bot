from __future__ import annotations

# Core Imports
import traceback
from typing import Optional, Tuple

# Third Party Packages
import aiohttp
import discord
from discord.ext import commands
from prisma import Prisma

# Local Imports
from cogs import COGS
from helpers.ipc.routes import ExultBotIPC
from helpers.logger import Logger
from helpers.regex import RegEx
from helpers.tree import Tree


class ExultBot(commands.Bot):
    """The main Discord Bot class"""

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

        # Setting this decides who can use owner-only commands such as jsk
        self.owner_ids = {
            957437570546012240,  # ExHiraku
            268815279570681857,  # lukewain
        }

    async def setup_hook(self) -> None:
        """
        A coroutine to be called to setup the bot after logging in
        but before we connect to the Discord Websocket.

        Mainly used to load our cogs / extensions.
        """
        # Jishaku is our debugging tool installed from PyPi
        await self.load_extension("jishaku")
        loaded_cogs = 1

        # Looping through and loading our local extensions (cogs)
        for cog in COGS:
            try:
                await self.load_extension(cog)
                loaded_cogs += 1
            except Exception as e:
                tb = traceback.format_exc()
                self.logger.error(f"{type(e)} Exception in loading {cog}\n{tb}")
                continue

        self.logger.info(f"Successfully loaded {loaded_cogs}/{len(COGS)+1} cogs!")

    async def on_ready(self) -> None:
        """
        A coroutine to be called every time the bot connects to the
        Discord Websocket.

        This can be called multiple times if the bot disconnects and
        reconnects, hence why we create the `_is_ready` class variable
        to prevent functionality that should only take place on our first
        start-up from happening again.
        """
        if self._is_ready:
            # Bot has disconnected and reconnected to the Websocket.
            return self.logger.critical("Bot reconnected to Discord Gateway.")

        # Our first time connecting to the Discord Websocket this session
        if self.sync_on_ready and len(self.guilds_to_sync):
            # If we prompted the bot to sync our app commands through command flags
            if -1 in self.guilds_to_sync:
                # Sync all global app commands
                try:
                    global_synced = await self.tree.sync()
                    self.logger.info(f"Synced {len(global_synced)} global commands!")
                except:
                    tb = traceback.format_exc()
                    self.logger.critical(
                        f"Failed to sync global application commands!\n{tb}"
                    )
            for guild_id in [g for g in self.guilds_to_sync if g != -1]:
                # Syncing guild-specific app commands
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

        # The bot is now fully setup and ready!
        self._is_ready = True
        self.logger.info(f"{self.user} is now online!")

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        """
        Logs in the client with the specified credentials and calls the :meth:`setup_hook` method
        then creates a websocket connection and lets the websocket listen to messages / events
        from Discord.
        """
        self.logger.info("Starting Bot...")
        async with aiohttp.ClientSession() as self.session, Prisma() as self.db, ExultBotIPC(
            self
        ) as self.ipc:
            # Initialises our ClientSession, Database connection and IPC server as bot variables.
            try:
                await super().start(token, reconnect=reconnect)
            finally:
                self.logger.info("Shutdown Bot.")

    def get_partial_emoji_with_state(
        self, name: str, animated: bool = False, id: Optional[int] = None
    ) -> discord.PartialEmoji:
        """
        A method that converts a string representation of an emoji to a
        :class:`PartialEmoji` using the bot's connection state.

        We call this through a bot method because the connection state is
        private to our bot class and should not be accessed externally.
        """
        return discord.PartialEmoji.with_state(
            self._connection, name=name, animated=animated, id=id
        )

    async def get_or_fetch_user(self, user_id: int) -> Optional[discord.User]:
        """
        A coroutine that attempts to retrieve a :class:`~discord.User` based on their ID
        from the bot's user cache.

        If the user cannot be found then it attempts to fetch the user directly from
        the Discord API.
        """
        try:
            return self.get_user(user_id) or await self.fetch_user(user_id)
        except discord.HTTPException:
            # If this exception is called then the ID provided does not correlate
            # to an existing Discord User
            return None
