from __future__ import annotations

# Core Imports
from ast import literal_eval
from typing import Any, Dict, List, Optional, Sequence, TYPE_CHECKING

# Third Party Imports
import discord

# Local Imports
from helpers import ui
from helpers.embed import Embed
from ..embeds import MessageBuilderEmbed, MessageManagerEmbed

# Type Imports
if TYPE_CHECKING:
    from helpers.types import ExultInteraction
    from ..types import MessageBuilderData

__all__ = ("MessageManager",)

CURRENT_MESSAGES = 2

# Pre-defining these buttons so we don't have an excessive amount of instances of ui.DeleteMessage
CANCEL_BUTTON: ui.Button[ui.View] = ui.DeleteMessage(
    style=discord.ButtonStyle.red, label="Cancel"
)
CANCEL_BUTTON_1: ui.Button[ui.View] = ui.DeleteMessage(
    style=discord.ButtonStyle.red, label="Cancel", row=1
)
CANCEL_BUTTON_2: ui.Button[ui.View] = ui.DeleteMessage(
    style=discord.ButtonStyle.red, label="Cancel", row=2
)


class ViewFactory:
    """
    View Factory that allows us to 'Lazy Load' views and components.
    Using this prevents Recursion Errors occurring.
    """

    @staticmethod
    def create_manager_view(ctx: ExultInteraction) -> MessageManager:
        return MessageManager(ctx)

    @staticmethod
    def create_builder_view(
        ctx: ExultInteraction, data: Optional[MessageBuilderData] = None
    ) -> MessageBuilderView:
        return MessageBuilderView(ctx, data)

    @staticmethod
    def create_selector_view(ctx: ExultInteraction) -> MessageSelectorView:
        return MessageSelectorView(ctx)

    @staticmethod
    def create_send_view(
        ctx: ExultInteraction, data: MessageBuilderData
    ) -> SendMessageView:
        return SendMessageView(ctx, data)

    @staticmethod
    def create_content_modal(
        ctx: ExultInteraction, data: MessageBuilderData, view: ui.View
    ) -> MessageContentModal:
        return MessageContentModal(ctx, data, view)

    @staticmethod
    def create_json_modal(
        ctx: ExultInteraction, data: MessageBuilderData, view: ui.View
    ) -> JSONEditorModal:
        return JSONEditorModal(ctx, data, view)


class PlaceholderButton(ui.Button[ui.V]):
    async def callback(self, itr: ExultInteraction) -> None:
        await itr.response.send_message(self.label, ephemeral=True)


class MessageContentModal(ui.Modal):
    def __init__(
        self, ctx: ExultInteraction, data: MessageBuilderData, view: ui.View
    ) -> None:
        self.ctx = ctx
        self.data = data
        self.view = view
        super().__init__(title="Message Content")

        self.add_item(
            ui.TextInput(
                label="Message Content",
                style=discord.TextStyle.long,
                placeholder="My message content...",
                default=data["content"],
                max_length=2000,
            )
        )

    async def on_submit(self, itr: ExultInteraction) -> None:
        await itr.response.defer(ephemeral=True)
        new_content = self.children[0].value
        if new_content == self.data["content"]:
            return await itr.followup.send("No changes were made.", ephemeral=True)
        self.data["content"] = new_content
        view = MessageBuilderView(self.ctx, self.data)
        await itr.edit_original_response(view=view)
        self.view.edited = True
        await itr.followup.send("Message Content has been updated!", ephemeral=True)


class JSONEditorModal(ui.Modal):
    def __init__(
        self, ctx: ExultInteraction, data: MessageBuilderData, view: ui.View
    ) -> None:
        try:
            self.ctx = ctx
            self.data = data
            self.view = view
            super().__init__(title="JSON Editor")

            shareable_data = {
                "content": data["content"] or "",
                "embeds": [e.to_dict() for e in data["embeds"]],
            }

            self.add_item(
                ui.TextInput(
                    label="JSON",
                    style=discord.TextStyle.long,
                    placeholder="{'content': 'My message content!', 'embeds': []}",
                    default=str(shareable_data),
                )
            )
        except Exception as e:
            print(f"{type(e)}: {e}")

    async def on_submit(self, itr: ExultInteraction) -> None:
        await itr.response.defer(ephemeral=True)
        user_json_str = self.children[0].value
        user_json_str.replace("null", "None").replace("true", "True").replace(
            "false", "False"
        )
        try:
            user_json: Dict[str, Any] = literal_eval(user_json_str)
        except Exception as e:
            return await itr.followup.send(
                f"Invalid JSON data provided.\n```py\n{type(e)}: {e}```", ephemeral=True
            )

        embeds: List[Embed] = []
        if "embed" in user_json and "embeds" in user_json:
            return await itr.followup.send(
                "Found both 'embed' and 'embeds' properties in JSON dictionary, "
                "please provide only of these 2 properties.",
                ephemeral=True,
            )
        if "embed" in user_json:
            if not isinstance(user_json["embed"], dict):
                return await itr.followup.send(
                    "Embed property must be a dictionary representing a valid discord Embed.",
                    ephemeral=True,
                )
            _embed: Dict[str, Any] = user_json["embed"]
            try:
                embed = await Embed.from_user_dict(itr.client, _embed)
            except Exception as e:
                return await itr.followup.send(str(e), ephemeral=True)
            embeds.append(embed)
        elif "embeds" in user_json:
            if not isinstance(user_json["embeds"], Sequence):
                return await itr.followup.send(
                    "Embeds property must be an array of dictionaries representing a valid discord Embed.",
                    ephemeral=True,
                )
            _embeds: Sequence[Any] = user_json["embeds"]
            for pos, _embed_item in enumerate(_embeds):
                if not isinstance(_embed_item, dict):
                    return await itr.followup.send(
                        f"Embed {pos} must be a dictionary representing a valid discord Embed.",
                        ephemeral=True,
                    )
                _embed_data: Dict[str, Any] = _embed_item
                try:
                    embed = await Embed.from_user_dict(itr.client, _embed_data)
                except Exception as e:
                    return await itr.followup.send(
                        f"Embed `{pos}`: {e}", ephemeral=True
                    )
                embeds.append(embed)
        self.data["content"] = user_json.get("content", None)
        self.data["embeds"] = embeds
        view = MessageBuilderView(self.ctx, self.data)
        await itr.edit_original_response(view=view)
        self.view.edited = True
        await itr.followup.send("Successfully updated message data!", ephemeral=True)


class SendMessageSelect(ui.ChannelSelect[ui.V]):
    def __init__(self, ctx: ExultInteraction, data: MessageBuilderData) -> None:
        self.ctx = ctx
        self.data = data

        super().__init__(
            channel_types=[discord.ChannelType.text],
            placeholder="Where shall we send your message?",
        )

    async def callback(self, itr: ExultInteraction) -> None:
        assert itr.guild
        channel = itr.guild.get_channel(self.values[0].id)
        if not channel:
            return await itr.response.send_message(
                "Selected channel no longer exists.", ephemeral=True
            )
        elif not isinstance(channel, discord.TextChannel):
            return await itr.response.send_message(
                "Selected channel must be a valid Discord Text Channel.", ephemeral=True
            )

        await itr.response.defer(ephemeral=True)

        if not channel.permissions_for(itr.guild.me).read_messages:
            return await itr.followup.send(
                f"I do not have permission to read messages in {channel.mention}.",
                ephemeral=True,
            )
        elif not channel.permissions_for(itr.guild.me).send_messages:
            return await itr.followup.send(
                f"I do not have permission to send messages in {channel.mention}.",
                ephemeral=True,
            )
        if len(self.data["embeds"]):
            if not channel.permissions_for(itr.guild.me).embed_links:
                return await itr.followup.send(
                    f"I do not have permission to embed messages in {channel.mention}.",
                    ephemeral=True,
                )

        try:
            msg = await channel.send(self.data["content"], embeds=self.data["embeds"])
        except Exception as e:
            return await itr.followup.send(
                f"Failed to send message to {channel.mention}: `{e}`", ephemeral=True
            )
        
        


class SendMessageView(ui.View):
    def __init__(self, ctx: ExultInteraction, data: MessageBuilderData) -> None:
        super().__init__(ctx, personal=True)

        self.add_item(SendMessageSelect(ctx, data))
        self.add_item(
            ui.GoToButton(
                style=discord.ButtonStyle.red,
                label="Go Back",
                row=1,
                edit_type="message",
                embed=MessageManagerEmbed,
                view=MessageBuilderView(ctx, data),
            )
        )
        self.add_item(CANCEL_BUTTON)


class MessageBuilderView(ui.View):
    def __init__(
        self, ctx: ExultInteraction, data: Optional[MessageBuilderData] = None
    ) -> None:
        try:
            super().__init__(ctx, personal=True)
            assert ctx.guild
            data = data or {
                "guild_id": ctx.guild.id,
                "content": None,
                "embeds": [],
                "edit": None,
            }

            ready = any((bool(data["content"]), len(data["embeds"])))

            self.add_item(
                ui.ModalButton(
                    lambda: ViewFactory.create_content_modal(ctx, data, self),
                    style=ui.COMPLETED_STYLE[bool(data["content"])],
                    label="Message Content",
                    emoji="📃",
                )
            )
            self.add_item(PlaceholderButton(label="Embeds", emoji="📰"))
            self.add_item(
                ui.ModalButton(
                    lambda: ViewFactory.create_json_modal(ctx, data, self),
                    style=discord.ButtonStyle.gray,
                    label="JSON Editor",
                    emoji="📎",
                )
            )
            self.add_item(PlaceholderButton(label="Save and Exit", emoji="💨", row=1))
            self.add_item(PlaceholderButton(label="Save and Send", emoji="💌", row=1))
            self.add_item(
                ui.GoToButton(
                    style=ui.COMPLETED_STYLE[ready],
                    label="Send without Saving",
                    disabled=not ready,
                    emoji="📨",
                    edit_type="message",
                    row=1,
                    view_factory=lambda: ViewFactory.create_send_view(ctx, data),
                )
            )
            self.add_item(
                ui.GoToButton(
                    style=discord.ButtonStyle.red,
                    label="Go Back",
                    row=2,
                    edit_type="message",
                    embed=MessageManagerEmbed,
                    view=MessageManager(ctx),
                )
            )
            self.add_item(CANCEL_BUTTON_2)
        except Exception as e:
            print(f"Error building View {type(e)}: ", e)


class MessageSelector(ui.Select[ui.V]):
    def __init__(self) -> None:
        super().__init__(
            placeholder="Select a message!",
            options=[
                discord.SelectOption(
                    label="Example",
                    value="example",
                    description="This does nothing",
                    emoji="💀",
                )
            ],
        )

    async def callback(self, itr: ExultInteraction) -> None:
        await itr.response.send_message("Example", ephemeral=True)


class MessageSelectorView(ui.View):
    def __init__(self, ctx: ExultInteraction) -> None:
        super().__init__(ctx, personal=True)

        self.add_item(MessageSelector())
        self.add_item(
            ui.GoToButton(
                style=discord.ButtonStyle.red,
                label="Go Back",
                row=2,
                edit_type="message",
                embed=MessageManagerEmbed,
                view=MessageManager(ctx),
            )
        )
        self.add_item(CANCEL_BUTTON)


class MessageManager(ui.View):
    def __init__(self, ctx: ExultInteraction) -> None:
        super().__init__(ctx, personal=True)

        buttons: List[Dict[str, Any]] = [
            {
                "style": discord.ButtonStyle.green,
                "label": "Create Message",
                "disabled": CURRENT_MESSAGES >= 10,
                "emoji": "➕",
                "embed": MessageBuilderEmbed,
                "view_factory": lambda: ViewFactory.create_builder_view(ctx),
            },
            {
                "style": discord.ButtonStyle.blurple,
                "label": "Edit Message",
                "disabled": CURRENT_MESSAGES <= 0,
                "emoji": "🛠️",
                "view_factory": lambda: ViewFactory.create_selector_view(ctx),
            },
            {
                "style": discord.ButtonStyle.red,
                "label": "Delete Message",
                "disabled": CURRENT_MESSAGES <= 0,
                "emoji": "🗑️",
                "view_factory": lambda: ViewFactory.create_selector_view(ctx),
            },
            {
                "style": discord.ButtonStyle.gray,
                "label": "View Message",
                "disabled": CURRENT_MESSAGES <= 0,
                "emoji": "👁️",
                "view_factory": lambda: ViewFactory.create_selector_view(ctx),
            },
        ]

        for kwargs in buttons:
            self.add_item(ui.GoToButton(**kwargs, edit_type="message"))

        self.add_item(ui.URLButton("Help", "https://bot.exultsoftware.com", "❔", row=1))
        self.add_item(
            ui.URLButton("Web Dashboard", "https://bot.exultsoftware.com", "🌐", row=1)
        )
        self.add_item(CANCEL_BUTTON_1)
