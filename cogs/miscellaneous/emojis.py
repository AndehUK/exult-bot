from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import discord
from discord import app_commands

from helpers.checks import is_image_valid
from helpers.cog import Cog
from helpers.colour import Colours
from helpers.embed import Embed
from helpers.transformers import GuildEmojiTransformer


if TYPE_CHECKING:
    from bot import ExultBot


class Emojis(Cog):
    emoji = app_commands.Group(
        name="emoji",
        description="Emoji Handler",
        guild_only=True,
        default_permissions=discord.Permissions(manage_expressions=True),
    )

    @emoji.command(name="add", description="Add an emoji to the server!")
    @app_commands.describe(
        name="The name of the emoji",
        emoji="The custom emoji or direct image url that you want the new emoji to be",
    )
    async def emoji_add(
        self, itr: discord.Interaction[ExultBot], name: str, emoji: str
    ) -> None:
        assert itr.guild

        is_url = itr.client.regex.url_regex.search(emoji)
        is_emoji = itr.client.regex.emoji_regex.search(emoji)

        if not is_url and not is_emoji:
            return await itr.response.send_message(
                f"Invalid emoji data provided. Please provide either an image url or a custom discord emoji!",
                ephemeral=True,
            )

        emoji_bytes = None
        await itr.response.defer()

        if is_url:
            # Check that the url leads to an image
            valid_image = await is_image_valid(itr.client, emoji)
            if not valid_image:
                return await itr.response.send_message(
                    "Please provide a valid image URL!", ephemeral=True
                )

            # Fetch the image data
            async with itr.client.session.request("GET", emoji) as request:
                emoji_bytes = await request.read()
        elif is_emoji:
            try:
                animated, emoji_name, emoji_id = is_emoji.groups()
                animated = animated.lower() == "a"
                result = itr.client.get_partial_emoji_with_state(
                    emoji_name, animated, int(emoji_id)
                )
                emoji_bytes = await result.read()
            except Exception as e:
                return await itr.response.send_message(e, ephemeral=True)

        if not emoji_bytes:
            return await itr.followup.send(
                "Failed to fetch image data.", ephemeral=True
            )

        try:
            new_emoji = await itr.guild.create_custom_emoji(
                name=name, image=emoji_bytes
            )
        except discord.Forbidden:
            return await itr.followup.send(
                "Oops! It seems I do not have permissions to create emojis in this server.",
                ephemeral=True,
            )
        except:
            return await itr.followup.send(
                "Something went wrong whilst attempting to create that emoji.",
                ephemeral=True,
            )

        embed = Embed(
            description=f"Successfully created the emoji: {new_emoji}!",
            colour=Colours.green,
        )
        await itr.followup.send(embed=embed)

    @emoji.command(name="delete", description="Delete an emoji from the server")
    @app_commands.describe(emoji="The name of the emoji you want to delete.")
    @app_commands.rename(emoji="name")
    async def emoji_delete(
        self,
        itr: discord.Interaction[ExultBot],
        emoji: app_commands.Transform[Optional[discord.Emoji], GuildEmojiTransformer],
    ):
        if not emoji:
            return await itr.response.send_message(
                "An emoji with that name does not exist in this server!", ephemeral=True
            )
        try:
            await emoji.delete()
            embed = Embed(
                description=f"Successfully deleted the emoji: `{emoji.name}`",
                colour=Colours.red,
            )
            await itr.response.send_message(embed=embed)
        except discord.Forbidden:
            await itr.response.send_message(
                "Oops! It seems I do not have permissions to delete emojis in this server.",
                ephemeral=True,
            )
        except:
            await itr.response.send_message(
                "Something went wrong whilst attempting to delete that emoji.",
                ephemeral=True,
            )
