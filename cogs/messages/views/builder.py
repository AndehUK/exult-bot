from __future__ import annotations

# Core Imports
from ast import literal_eval
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    TypeVar,
    TYPE_CHECKING,
    Union,
)

# Third Party Imports
import discord

# Local Imports
from helpers import ui
from helpers.checks import is_image_valid
from helpers.colour import Colours
from helpers.embed import Embed, EmbedField
from ..embeds import MessageBuilderEmbed, MessageManagerEmbed, SuccessEmbed

# Type Imports
if TYPE_CHECKING:
    from helpers.types import ExultInteraction
    from ..types import MessageBuilderData

__all__ = ("MessageManager",)

EFB = TypeVar("EFB", bound="EmbedFieldBuilder")
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
    def create_embed_builder_view(
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Optional[Embed] = None,
    ) -> EmbedBuilderView:
        return EmbedBuilderView(ctx, data, embed_data)

    @staticmethod
    def create_embed_author_modal(
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        view: ui.View,
    ) -> EmbedAuthorModal:
        return EmbedAuthorModal(ctx, data, embed_data, view)

    @staticmethod
    def create_embed_title_modal(
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        view: ui.View,
    ) -> EmbedTitleModal:
        return EmbedTitleModal(ctx, data, embed_data, view)

    @staticmethod
    def create_embed_description_modal(
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        view: ui.View,
    ) -> EmbedDescriptionModal:
        return EmbedDescriptionModal(ctx, data, embed_data, view)

    @staticmethod
    def create_embed_colour_modal(
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        view: ui.View,
    ) -> EmbedColourModal:
        return EmbedColourModal(ctx, data, embed_data, view)

    @staticmethod
    def create_embed_fields_view(
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
    ) -> EmbedFields:
        return EmbedFields(ctx, data, embed_data)

    @staticmethod
    def create_embed_field_prop_modal(
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        field_id: int,
        view: EmbedFieldBuilder,
        *,
        edit: Union[Literal["name"], Literal["value"]],
    ) -> EmbedFieldPropModal:
        return EmbedFieldPropModal(ctx, data, embed_data, field_id, view, edit=edit)

    @staticmethod
    def create_embed_field_builder_view(
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        field_id: Optional[int] = None,
        *,
        new: bool,
        pre_edit_state: Optional[EmbedField] = None,
    ) -> EmbedFieldBuilder:
        return EmbedFieldBuilder(
            ctx, data, embed_data, field_id, new=new, pre_edit_state=pre_edit_state
        )

    @staticmethod
    def create_embed_field_selector_view(
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        *,
        delete: bool = False,
    ) -> EmbedFieldSelectorView:
        return EmbedFieldSelectorView(ctx, data, embed_data, delete=delete)

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


class EmbedAuthorModal(ui.Modal):
    def __init__(
        self,
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        view: ui.View,
    ) -> None:
        self.ctx = ctx
        self.data = data
        self.embed_data = embed_data
        self.view = view

        super().__init__(title="Embed Author")

        self.add_item(
            ui.TextInput(
                label="Author Name",
                placeholder=ctx.user.name,
                default=embed_data.author.name,
                max_length=256,
            )
        )

        self.add_item(
            ui.TextInput(
                label="Author Icon URL",
                placeholder=ctx.user.display_avatar.url,
                default=embed_data.author.icon_url,
                required=False,
            )
        )

        self.add_item(
            ui.TextInput(
                label="Author URL",
                placeholder="https://bot.exultsoftware.com",
                default=embed_data.author.url,
                required=False,
            )
        )

    async def on_submit(self, itr: ExultInteraction) -> None:
        await itr.response.defer(ephemeral=True)

        author_name = self.children[0].value
        author_icon = None
        author_url = None

        name_changes: Optional[str] = None
        icon_changes: Optional[str] = None
        url_changes: Optional[str] = None

        name_changes = (
            "No changes were made to author name."
            if self.embed_data.author.name == author_name
            else f"Author name has been updated to `{author_name}`."
        )

        if self.children[1].value == self.embed_data.author.icon_url:
            icon_changes = "No changes were made to author icon."
            author_icon = self.children[1].value
        else:
            if self.children[1].value:
                valid_url = itr.client.regex.url_regex.search(self.children[1].value)
                if not valid_url:
                    icon_changes = "Invalid URL provided for author icon."
                else:
                    valid_image = await is_image_valid(
                        itr.client, self.children[1].value
                    )
                    if not valid_image:
                        icon_changes = "Invalid image provided for author icon."
                    else:
                        icon_changes = "Author icon has been updated."
                        author_icon = self.children[1].value
            else:
                icon_changes = "No author icon was provided."

        if self.children[2].value == self.embed_data.author.url:
            url_changes = "No changes were made to author URL."
            author_url = self.children[2].value
        else:
            if self.children[2].value:
                valid_url = itr.client.regex.url_regex.search(self.children[2].value)
                if not valid_url:
                    url_changes = "Invalid URL provided for author URL."
                else:
                    url_changes = "Author URL has been updated."
                    author_url = self.children[2].value
            else:
                url_changes = "No author URL was provided."

        embed = Embed(
            description=f"## Updated Embed Author:\n{name_changes}\n{icon_changes}\n{url_changes}",
            colour=Colours.green,
        )
        self.embed_data.set_author(
            name=author_name, icon_url=author_icon, url=author_url
        )
        view = EmbedBuilderView(self.ctx, self.data, self.embed_data)
        await itr.edit_original_response(view=view)
        self.view.edited = True
        await itr.followup.send(embed=embed, ephemeral=True)


class EmbedTitleModal(ui.Modal):
    def __init__(
        self,
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        view: ui.View,
    ) -> None:
        self.ctx = ctx
        self.data = data
        self.embed_data = embed_data
        self.view = view
        super().__init__(title="Embed Title")

        self.add_item(
            ui.TextInput(
                label="Title",
                placeholder="My Embed Title",
                default=embed_data.title,
                max_length=256,
            )
        )

        self.add_item(
            ui.TextInput(
                label="Title URL",
                placeholder="https://bot.exultsoftware.com",
                default=embed_data.url,
                required=False,
            )
        )

    async def on_submit(self, itr: ExultInteraction) -> None:
        await itr.response.defer(ephemeral=True)

        title = self.children[0].value
        title_url = None

        title_changes: Optional[str] = None
        url_changes: Optional[str] = None

        title_changes = (
            "No changes were made to embed title."
            if self.embed_data.title == title
            else f"Embed title has been updated to `{title}`."
        )

        if self.children[1].value == self.embed_data.url:
            url_changes = "No changes were made to embed title URL."
            title_url = self.children[1].value
        else:
            if self.children[1].value:
                valid_url = itr.client.regex.url_regex.search(self.children[1].value)
                if not valid_url:
                    url_changes = "Invalid URL provided for embed title URL."
                else:
                    url_changes = "Embed title URL has been updated."
                    title_url = self.children[1].value
            else:
                url_changes = "No embed title URL was provided."

        embed = Embed(
            description=f"## Updated Embed Title:\n{title_changes}\n{url_changes}",
            colour=Colours.green,
        )
        self.embed_data.title = title
        self.embed_data.url = title_url
        view = EmbedBuilderView(self.ctx, self.data, self.embed_data)
        await itr.edit_original_response(view=view)
        self.view.edited = True
        await itr.followup.send(embed=embed, ephemeral=True)


class EmbedDescriptionModal(ui.Modal):
    def __init__(
        self,
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        view: ui.View,
    ) -> None:
        self.ctx = ctx
        self.data = data
        self.embed_data = embed_data
        self.view = view
        super().__init__(title="Embed Description")

        self.add_item(
            ui.TextInput(
                label="Description",
                style=discord.TextStyle.paragraph,
                placeholder="My Embed Description",
                default=embed_data.description,
                max_length=2048,
            )
        )

    async def on_submit(self, itr: ExultInteraction) -> None:
        await itr.response.defer(ephemeral=True)

        description = self.children[0].value

        description_changes: Optional[str] = None

        description_changes = (
            "No changes were made to embed description."
            if self.embed_data.description == description
            else f"Embed description has been updated to `{description}`."
        )

        embed = Embed(
            description=f"## Updated Embed Description:\n{description_changes}",
            colour=Colours.green,
        )
        self.embed_data.description = description
        view = EmbedBuilderView(self.ctx, self.data, self.embed_data)
        await itr.edit_original_response(view=view)
        self.view.edited = True
        await itr.followup.send(embed=embed, ephemeral=True)


class EmbedColourModal(ui.Modal):
    def __init__(
        self,
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        view: ui.View,
    ) -> None:
        self.ctx = ctx
        self.data = data
        self.embed_data = embed_data
        self.view = view
        super().__init__(title="Embed Colour")

        self.add_item(
            ui.TextInput(
                label="Colour",
                placeholder="#000000",
                default=f"rgb{str(embed_data.colour.to_rgb())}"
                if embed_data.colour
                else "#",
                max_length=25,
            )
        )

    async def on_submit(self, itr: ExultInteraction) -> None:
        await itr.response.defer(ephemeral=True)

        new_colour = str(self.children[0].value).lower()  # type: ignore

        colour_changes: Optional[str] = None

        colour = (
            f"#{new_colour}"
            if all((not new_colour.startswith("#"), not new_colour.startswith("rgb")))
            else new_colour
        )
        if colour.startswith("##"):
            colour = colour[1:]
        try:
            colour = discord.Colour.from_str(colour)
            colour_changes = f"Embed colour has been updated to `{colour}`."
        except ValueError:
            embed = Embed(
                colour=Colours.red,
                description="## Invalid colour value given.\n Please ensure you provide either a **__Hex Code__** or **__RGB__** value.\n### Example:\n- rgb(102, 142, 255)\n- #668EFF",
            )
            return await itr.followup.send(embed=embed, ephemeral=True)

        colour_changes = (
            "No changes were made to embed colour."
            if self.embed_data.colour == colour
            else f"Embed colour has been updated to `{colour}`."
        )

        self.embed_data.colour = colour

        embed = Embed(
            description=f"## Updated Embed Colour: \n{colour_changes}",
            colour=colour,
        )
        view = EmbedBuilderView(self.ctx, self.data, self.embed_data)
        await itr.edit_original_response(view=view)
        self.view.edited = True
        await itr.followup.send(embed=embed, ephemeral=True)


class EmbedFieldPropModal(ui.Modal):
    def __init__(
        self,
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        field_id: int,
        view: EmbedFieldBuilder,
        *,
        edit: Union[Literal["name"], Literal["value"]],
    ) -> None:
        self.ctx = ctx
        self.data = data
        self.embed_data = embed_data
        self.view: EmbedFieldBuilder = view
        self.field_id = field_id
        self.edit = edit
        self.field = embed_data.fields[field_id]
        if not self.field:
            raise ValueError("Invalid Embed Field Detected")
        label = "Field Name" if edit == "name" else "Field Value"
        prop = self.field.name if edit == "name" else self.field.value
        max_length = 256 if edit == "name" else 1024
        super().__init__(title=f"Embed {label}")

        self.add_item(ui.TextInput(label=label, default=prop, max_length=max_length))

    async def on_submit(self, itr: ExultInteraction) -> None:
        await itr.response.defer(ephemeral=True)

        if not self.field:
            raise ValueError("Invalid Embed Field Detected")
        new_prop = self.children[0].value
        old_prop = self.field.name if self.edit == "name" else self.field.value
        field = self.embed_data.fields[self.field_id]
        if not field:
            raise ValueError("Invalid Embed Field Detected")
        prop_changes = (
            f"No changes were made to field {self.edit}."
            if old_prop == new_prop
            else f"Field {self.edit} has been updated to `{new_prop}`."
        )
        self.embed_data.set_field_at(
            self.field_id,
            name=new_prop if self.edit == "name" else self.field.name,
            value=new_prop if self.edit == "value" else self.field.value,
            inline=self.field.inline,
        )
        view = EmbedFieldBuilder(
            self.ctx,
            self.data,
            self.embed_data,
            self.field_id,
            new=self.view.new,
            pre_edit_state=self.view.pre_edit_state,
        )
        embed = Embed(
            description=f"## Updated Embed Field {self.edit.capitalize()}:\n {prop_changes}",
            colour=Colours.green,
        )
        await itr.edit_original_response(view=view)
        self.view.edited = True
        await itr.followup.send(embed=embed, ephemeral=True)


class EmbedFieldInlineToggle(ui.Button[EFB]):
    def __init__(
        self,
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        *,
        field_id: int,
    ) -> None:
        self.ctx = ctx
        self.data = data
        self.embed_data = embed_data
        self.field_id = field_id
        self.field = embed_data.fields[field_id]
        if not self.field:
            raise ValueError("Invalid Embed Field Detected")
        self.inline = self.field.inline
        label = "Inline" if self.field.inline else "Not Inline"
        super().__init__(style=ui.STATUS_STYLE[self.inline], label=label)

    async def callback(self, itr: ExultInteraction) -> None:
        await itr.response.defer(ephemeral=True)
        new_inline = not self.inline

        if not self.field:
            raise ValueError("Invalid Embed Field Detected")
        self.embed_data.set_field_at(
            self.field_id,
            name=self.field.name,
            value=self.field.value,
            inline=new_inline,
        )
        view = EmbedFieldBuilder(
            self.ctx,
            self.data,
            self.embed_data,
            self.field_id,
            new=self.view.new,
            pre_edit_state=self.view.pre_edit_state,
        )
        new_status = "`✅` Inline" if new_inline else "`❌` Not Inline"
        embed = Embed(
            description=f"## Updated Embed Field Inline:\n {new_status}",
            colour=Colours.green,
        )
        await itr.edit_original_response(view=view)
        self.view.edited = True
        await itr.followup.send(embed=embed, ephemeral=True)


class EmbedFieldConfirm(ui.Button[EFB]):
    def __init__(
        self,
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        *,
        field_id: int,
    ) -> None:
        self.ctx = ctx
        self.data = data
        self.embed_data = embed_data
        self.field_id = field_id
        field = embed_data.fields[field_id]
        if not field:
            raise ValueError("Invalid Embed Field Detected")
        ready = all((field.name != "\u200b", field.value != "\u200b"))
        super().__init__(
            style=ui.COMPLETED_STYLE[ready], label="Confirm", disabled=not ready, row=1
        )

    async def callback(self, itr: ExultInteraction) -> None:
        await itr.response.defer(ephemeral=True)

        action = "created" if not self.view.new else "updated"
        view = EmbedBuilderView(self.ctx, self.data, self.embed_data)
        embed = Embed(
            description=f"## Embed Field {action}:\n Field {len(self.embed_data.fields)} has been {action}!",
            colour=Colours.green,
        )
        await itr.edit_original_response(view=view)
        self.view.edited = True
        await itr.followup.send(embed=embed, ephemeral=True)


class EmbedFieldBuilder(ui.View):
    new: bool
    pre_edit_state: Optional[EmbedField]

    def __init__(
        self,
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        field_id: Optional[int] = None,
        *,
        new: bool,
        pre_edit_state: Optional[EmbedField] = None,
    ) -> None:
        self.new = new
        self.pre_edit_state = pre_edit_state
        if field_id is None:
            embed_data = embed_data.add_invisible_field()
            field_id = -1
        field = embed_data.fields[field_id]
        if not field:
            raise ValueError("Invalid Embed Field Detected")
        super().__init__(ctx, personal=True)
        self.add_item(
            ui.ModalButton(
                lambda: ViewFactory.create_embed_field_prop_modal(
                    ctx, data, embed_data, field_id, self, edit="name"
                ),
                style=ui.COMPLETED_STYLE[
                    all((field.name != None, field.name != "\u200b"))
                ],
                label="Field Name",
            )
        )
        self.add_item(
            ui.ModalButton(
                lambda: ViewFactory.create_embed_field_prop_modal(
                    ctx, data, embed_data, field_id, self, edit="value"
                ),
                style=ui.COMPLETED_STYLE[
                    all((field.value != None, field.value != "\u200b"))
                ],
                label="Field Value",
            )
        )
        self.add_item(EmbedFieldInlineToggle(ctx, data, embed_data, field_id=field_id))
        self.add_item(EmbedFieldConfirm(ctx, data, embed_data, field_id=field_id))
        self.add_item(
            ui.GoToButton(
                style=discord.ButtonStyle.red,
                label="Go Back",
                row=1,
                edit_type="message",
                embed=MessageManagerEmbed,
                view=EmbedBuilderView(ctx, data, embed_data),
            )
        )
        self.add_item(CANCEL_BUTTON_1)


class EmbedFieldSelector(ui.Select[ui.V]):
    def __init__(
        self,
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        *,
        delete: bool = False,
    ) -> None:
        self.ctx = ctx
        self.data = data
        self.embed_data = embed_data
        self.delete = delete
        options = [
            discord.SelectOption(label=f.name, value=str(pos))
            for pos, f in enumerate(embed_data.fields)
            if f.name
        ]

        super().__init__(
            placeholder="Select an Embed Field!",
            max_values=len(embed_data.fields) if delete else 1,
            options=options,
        )

    async def callback(self, itr: ExultInteraction) -> None:
        await itr.response.defer(ephemeral=True)

        if self.delete:
            total = 0
            for pos in sorted([int(v) for v in self.values], reverse=True):
                del self.embed_data.fields[pos]
                total += 1
            description = (
                f"Successfully deleted {total}/{len(self.values)} embed fields."
            )
            embed = Embed(
                description=f"## Embed Fields Deleted:\n{description}",
                colour=Colours.green,
            )
            await itr.followup.send(embed=embed, ephemeral=True)
            view = EmbedBuilderView(self.ctx, self.data, self.embed_data)
        else:
            pos = int(self.values[0])
            field = self.embed_data.fields[pos]
            assert field
            view = EmbedFieldBuilder(
                self.ctx, self.data, self.embed_data, field_id=pos, new=False
            )
        await itr.edit_original_response(view=view)


class EmbedFieldSelectorView(ui.View):
    def __init__(
        self,
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
        *,
        delete: bool = False,
    ) -> None:
        super().__init__(ctx, personal=True)

        self.add_item(EmbedFieldSelector(ctx, data, embed_data, delete=delete))
        self.add_item(
            ui.GoToButton(
                style=discord.ButtonStyle.red,
                label="Go Back",
                row=1,
                edit_type="message",
                embed=MessageManagerEmbed,
                view=EmbedFields(ctx, data, embed_data),
            )
        )
        self.add_item(CANCEL_BUTTON_1)


class EmbedFields(ui.View):
    def __init__(
        self,
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Embed,
    ) -> None:
        super().__init__(ctx, personal=True)

        self.add_item(
            ui.GoToButton(
                style=discord.ButtonStyle.green,
                label="Add Field",
                row=1,
                edit_type="message",
                embed=MessageManagerEmbed,
                view_factory=lambda: ViewFactory.create_embed_field_builder_view(
                    ctx, data, embed_data, new=True
                ),
            )
        )
        self.add_item(
            ui.GoToButton(
                style=discord.ButtonStyle.blurple,
                label="Edit Field",
                row=1,
                edit_type="message",
                embed=MessageManagerEmbed,
                view_factory=lambda: ViewFactory.create_embed_field_selector_view(
                    ctx, data, embed_data, delete=False
                ),
            )
        )
        self.add_item(
            ui.GoToButton(
                style=discord.ButtonStyle.red,
                label="Delete Field",
                row=1,
                edit_type="message",
                embed=MessageManagerEmbed,
                view_factory=lambda: ViewFactory.create_embed_field_selector_view(
                    ctx, data, embed_data, delete=True
                ),
            )
        )
        self.add_item(
            ui.GoToButton(
                style=discord.ButtonStyle.red,
                label="Go Back",
                row=2,
                edit_type="message",
                embed=MessageManagerEmbed,
                view=EmbedBuilderView(ctx, data, embed_data),
            )
        )
        self.add_item(CANCEL_BUTTON_2)


class EmbedBuilderConfirm(ui.Button[ui.V]):
    def __init__(
        self, ctx: ExultInteraction, data: MessageBuilderData, embed_data: Embed
    ) -> None:
        self.ctx = ctx
        self.data = data
        self.embed_data = embed_data
        super().__init__(
            style=ui.COMPLETED_STYLE[embed_data.is_minimal_ready()],
            label="Confirm",
            row=2,
            emoji="✅",
            disabled=not embed_data.is_minimal_ready(),
        )

    async def callback(self, itr: ExultInteraction) -> None:
        await itr.response.defer(ephemeral=True)
        if len(self.data["embeds"]) >= 10:
            return await itr.followup.send(
                "`❌` You have reached the maximum amount of embeds allowed per message.",
                ephemeral=True,
            )
        self.data["embeds"].append(self.embed_data)
        view = MessageBuilderView(self.ctx, self.data)
        await itr.edit_original_response(view=view)
        self.view.edited = True
        await itr.followup.send("Embed has been added to your message!", ephemeral=True)


class EmbedBuilderView(ui.View):
    def __init__(
        self,
        ctx: ExultInteraction,
        data: MessageBuilderData,
        embed_data: Optional[Embed] = None,
    ) -> None:
        super().__init__(ctx, personal=True)

        self.embed_data = embed_data or Embed()

        self.add_item(
            ui.ModalButton(
                lambda: ViewFactory.create_embed_author_modal(
                    ctx, data, self.embed_data, self
                ),
                style=ui.COMPLETED_STYLE[bool(self.embed_data.author.name)],
                label="Embed Author",
            )
        )
        self.add_item(
            ui.ModalButton(
                lambda: ViewFactory.create_embed_title_modal(
                    ctx, data, self.embed_data, self
                ),
                style=ui.COMPLETED_STYLE[bool(self.embed_data.title)],
                label="Embed Title",
            )
        )
        self.add_item(
            ui.ModalButton(
                lambda: ViewFactory.create_embed_description_modal(
                    ctx, data, self.embed_data, self
                ),
                style=ui.COMPLETED_STYLE[bool(self.embed_data.description)],
                label="Embed Description",
            )
        )
        self.add_item(
            ui.ModalButton(
                lambda: ViewFactory.create_embed_colour_modal(
                    ctx, data, self.embed_data, self
                ),
                style=ui.COMPLETED_STYLE[bool(self.embed_data.colour)],
                label="Embed Colour",
            )
        )
        self.add_item(
            ui.GoToButton(
                style=ui.COMPLETED_STYLE[bool(self.embed_data.fields)],
                label="Fields",
                disabled=len(self.embed_data.fields) >= 25,
                emoji="📰",
                view_factory=lambda: ViewFactory.create_embed_fields_view(
                    ctx, data, self.embed_data
                ),
            )
        )
        self.add_item  # Footer
        self.add_item  # Thumbnail
        self.add_item  # Image
        self.add_item(EmbedBuilderConfirm(ctx, data, self.embed_data))
        self.add_item(
            ui.GoToButton(
                style=discord.ButtonStyle.red,
                label="Go Back",
                row=2,
                edit_type="message",
                embed=MessageManagerEmbed,
                view=MessageBuilderView(ctx, data),
            )
        )
        self.add_item(CANCEL_BUTTON_2)


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
                "Selected channel must be a valid Discord Text Channel.",
                ephemeral=True,
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
                f"Failed to send message to {channel.mention}: `{e}`",
                ephemeral=True,
            )
        view = ui.View().add_item(ui.URLButton("Go to Message", msg.jump_url))
        await itr.edit_original_response(embed=SuccessEmbed(channel), view=view)
        self.view.edited = True


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
            self.add_item(
                ui.GoToButton(
                    style=ui.COMPLETED_STYLE[bool(data["embeds"])],
                    label="Embeds",
                    disabled=len(data["embeds"]) >= 10,
                    emoji="📰",
                    view_factory=lambda: ViewFactory.create_embed_builder_view(
                        ctx, data
                    ),
                )
            )
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
