from __future__ import annotations

# Core Imports
from typing import TYPE_CHECKING

# Third Party Packages
from aiohttp import web

# Local Imports
from .base import IPCBase, Methods, route
from .types import MinimalDiscordGuild, MinimalDiscordUser

# Type Imports
if TYPE_CHECKING:
    from discord import Guild, User


class ExultBotIPC(IPCBase):
    def _guild_to_dict(self, guild: Guild) -> MinimalDiscordGuild:
        """
        Returns a :class:`MinimalDiscordGuild` containing all the information about a
        given guild that our API needs
        """

        return {
            "channels": [
                {
                    "category": {"id": c.category.id, "name": c.category.name}
                    if c.category
                    else None,
                    "id": c.id,
                    "name": c.name,
                    "type": c.type.value,
                }
                for c in guild.channels
            ],
            "emojis": [],
            "icon": guild.icon.url if guild.icon else None,
            "id": guild.id,
            "name": guild.name,
            "owner_id": guild.owner_id,
            "premium_tier": guild.premium_tier,
            "roles": [],
            "unavailable": guild.unavailable,
        }

    def _user_to_dict(self, user: User) -> MinimalDiscordUser:
        """
        Returns a :class:`MinimalDiscordUser` containing all the information about a
        given guild that our API needs
        """

        return {
            "username": user.name,
            "id": user.id,
            "avatar": user.display_avatar.url,
            "global_name": user.global_name,
        }

    @route("/stats", method=Methods.get)
    async def stats(self, req: web.Request) -> web.Response:
        """Returns some basic statistics about Exult Bot"""

        return web.json_response(
            {
                "guilds": len(self.bot.guilds),
                "users": {
                    "total": sum(g.member_count or 0 for g in self.bot.guilds),
                    "unique": len(self.bot.users),
                },
            }
        )

    @route("/users/{id}", method=Methods.get)
    async def get_user(self, request: web.Request) -> web.Response:
        """Returns some basic information on a given user"""

        user_id = int(request.match_info["id"])
        user = await self.bot.get_or_fetch_user(user_id)
        if not user:
            return web.json_response({"error": "User not found."}, status=404)
        return web.json_response(self._user_to_dict(user))

    @route("/users/{id}/guilds", method=Methods.get)
    async def get_user_guilds(self, request: web.Request) -> web.Response:
        """Returns the guilds that Exult Bot shares with the given user"""

        user_id = int(request.match_info["id"])
        user = await self.bot.get_or_fetch_user(user_id)
        if not user:
            return web.json_response({"error": "User not found."}, status=404)
        user_data = self._user_to_dict(user)
        user_data["guilds"] = [self._guild_to_dict(g) for g in user.mutual_guilds]
        return web.json_response(user_data)
