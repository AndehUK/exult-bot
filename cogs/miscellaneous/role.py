from __future__ import annotations

import asyncio
import datetime
from typing import Optional, TYPE_CHECKING

import discord
from discord import app_commands

from helpers.checks import check_role_permissions
from helpers.cog import Cog
from helpers.colour import Colours
from helpers.embed import Embed

if TYPE_CHECKING:
    from helpers.types import ExultInteraction


class RoleUtility(Cog):
    role_group = app_commands.Group(
        name="role",
        description="Commands for managing roles",
        default_permissions=discord.Permissions(manage_roles=True),
        guild_only=True,
    )

    role_all = app_commands.Group(
        name="all",
        description="Commands for managing roles for all members",
        default_permissions=discord.Permissions(administrator=True),
        guild_only=True,
        parent=role_group,
    )

    @role_group.command(name="add", description="Adds a role to a member")
    async def role_add(
        self, itr: ExultInteraction, member: discord.Member, role: discord.Role
    ) -> None:
        assert itr.guild and isinstance(itr.user, discord.Member)

        if not await check_role_permissions(itr.guild, role, itr=itr, target=member):
            return
        if role in member.roles:
            await itr.response.send_message(
                f"{member.mention} already has the role {role.mention}!",
                ephemeral=True,
            )
            return
        try:
            await member.add_roles(role)
            await itr.response.send_message(
                f"Successfully added the role {role.mention} to {member.mention}!",
                ephemeral=True,
            )
        except Exception as e:
            await itr.response.send_message(
                f"Failed to add the role {role.mention} to {member.mention}! ~ {type(e).__name__}: {e}",
                ephemeral=True,
            )

    @role_group.command(name="remove", description="Removes a role from a member")
    async def role_remove(
        self, itr: ExultInteraction, member: discord.Member, role: discord.Role
    ) -> None:
        assert itr.guild and isinstance(itr.user, discord.Member)

        if not await check_role_permissions(itr.guild, role, itr=itr, target=member):
            return
        if role not in member.roles:
            await itr.response.send_message(
                f"{member.mention} doesn't have the role {role.mention}!",
                ephemeral=True,
            )
            return
        try:
            await member.remove_roles(role)
            await itr.response.send_message(
                f"Successfully removed the role {role.mention} from {member.mention}!",
                ephemeral=True,
            )
        except Exception as e:
            await itr.response.send_message(
                f"Failed to remove the role {role.mention} from {member.mention}! ~ {type(e).__name__}: {e}",
                ephemeral=True,
            )

    @role_all.command(name="add", description="Adds a role to all members")
    async def role_all_add(
        self,
        itr: ExultInteraction,
        role: discord.Role,
        with_role: Optional[discord.Role] = None,
        without_role: Optional[discord.Role] = None,
        include_bots: bool = True,
    ) -> None:
        assert itr.guild and isinstance(itr.user, discord.Member)

        if not await check_role_permissions(itr.guild, role, itr=itr):
            return

        members = (
            itr.guild.members
            if include_bots
            else [m for m in itr.guild.members if not m.bot]
        )
        if with_role and without_role:
            members = [
                m
                for m in members
                if with_role in m.roles and not without_role in m.roles
            ]
        elif with_role and not without_role:
            members = [m for m in members if with_role not in m.roles]
        elif not with_role and without_role:
            members = [m for m in members if without_role in m.roles]

        started = datetime.datetime.now(datetime.timezone.utc)
        eta = started + datetime.timedelta(seconds=len(members) * 3)
        formatted_started = discord.utils.format_dt(started, "R")
        formatted_eta = discord.utils.format_dt(eta, "R")

        embed = Embed(
            description=(
                f"## Assigning {role.mention} to {len(members)} members\n"
                f"Estimated time of completion: {formatted_eta}\n"
                "## Options"
            ),
            colour=Colours.gold,
        )
        embed.add_field(
            name="Include Bots", value="Yes" if include_bots else "No", inline=False
        )
        if with_role:
            embed.add_field(
                name="With Role",
                value=with_role.mention if with_role else "No role required",
                inline=False,
            )
        if without_role:
            embed.add_field(
                name="Without Role",
                value=without_role.mention if without_role else "No role required",
                inline=False,
            )
        await itr.followup.send(embed=embed)
        failed = 0
        for member in members:
            try:
                if role not in member.roles:
                    await member.add_roles(role)
                    await asyncio.sleep(3)
            except:
                failed += 1
        success = len(members) - failed
        embed.description = (
            f"## Assigned {role.mention} to {success} members\n"
            f"Estimated time of completion: {formatted_started}"
        )
        embed.colour = Colours.green
        await itr.edit_original_response(embed=embed)

    @role_all.command(name="remove", description="Removes a role from all members")
    async def role_all_remove(
        self,
        itr: ExultInteraction,
        role: discord.Role,
        with_role: Optional[discord.Role] = None,
        without_role: Optional[discord.Role] = None,
        include_bots: bool = True,
    ) -> None:
        assert itr.guild and isinstance(itr.user, discord.Member)

        if not await check_role_permissions(itr.guild, role, itr=itr):
            return

        members = (
            itr.guild.members
            if include_bots
            else [m for m in itr.guild.members if not m.bot]
        )
        if with_role and without_role:
            members = [
                m
                for m in members
                if with_role in m.roles and not without_role in m.roles
            ]
        elif with_role and not without_role:
            members = [m for m in members if with_role not in m.roles]
        elif not with_role and without_role:
            members = [m for m in members if without_role in m.roles]

        started = datetime.datetime.now(datetime.timezone.utc)
        eta = started + datetime.timedelta(seconds=len(members) * 3)
        formatted_started = discord.utils.format_dt(started, "R")
        formatted_eta = discord.utils.format_dt(eta, "R")

        embed = Embed(
            description=(
                f"## Removing {role.mention} from {len(members)} members\n"
                f"Estimated time of completion: {formatted_eta}\n"
                "## Options"
            ),
            colour=Colours.gold,
        )
        embed.add_field(
            name="Include Bots", value="Yes" if include_bots else "No", inline=False
        )
        if with_role:
            embed.add_field(
                name="With Role",
                value=with_role.mention if with_role else "No role required",
                inline=False,
            )
        if without_role:
            embed.add_field(
                name="Without Role",
                value=without_role.mention if without_role else "No role required",
                inline=False,
            )
        await itr.followup.send(embed=embed)
        failed = 0
        for member in members:
            try:
                if role in member.roles:
                    await member.remove_roles(role)
                    await asyncio.sleep(3)
            except:
                failed += 1
        success = len(members) - failed
        embed.description = (
            f"## Removed {role.mention} from {success} members\n"
            f"Estimated time of completion: {formatted_started}"
        )
        embed.colour = Colours.green
        await itr.edit_original_response(embed=embed)
