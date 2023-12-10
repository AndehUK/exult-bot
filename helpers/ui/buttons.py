from __future__ import annotations

# Core Imports
import traceback
from uuid import uuid4
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Literal,
    Optional,
    Sequence,
    TypeVar,
    TYPE_CHECKING,
    Union,
)

# Third Party Packages
import discord
from discord import ui
from discord.emoji import Emoji
from discord.enums import ButtonStyle
from discord.partial_emoji import PartialEmoji
from discord.utils import MISSING

# Local Imports
from .views import View

# Type Imports
if TYPE_CHECKING:
    from bot import ExultBot
    from helpers.embed import Embed

__all__ = ("Button", "GoToButton", "URLButton", "DeleteMessage", "ModalButton")


V = TypeVar("V", bound="View", covariant=True)


class Button(ui.Button[V], Generic[V]):
    """Represents a UI button."""

    view: V

    def __init__(
        self,
        *,
        style: discord.ButtonStyle = discord.ButtonStyle.secondary,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
        row: Optional[int] = None,
    ) -> None:
        custom_id = custom_id or f"{self.__class__.__name__}:{uuid4()}"

        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            url=None,
            emoji=emoji,
            row=row,
        )


class URLButton(ui.Button[V], Generic[V]):
    """Builds on :class:`discord.ui.Button` to easily generate a URL Button"""

    view: V

    def __init__(
        self,
        label: str,
        url: str,
        emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
        row: Optional[int] = None,
    ) -> None:
        super().__init__(
            style=discord.ButtonStyle.url, label=label, url=url, emoji=emoji, row=row
        )


class GoToButton(Button[V], Generic[V]):
    """
    Builds on :class:`helpers.ui.Button` to easily generate a button that
    navigates the user to another :class:`helpers.ui.View`.
    """

    view: V

    def __init__(
        self,
        *,
        style: discord.ButtonStyle = discord.ButtonStyle.secondary,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
        row: Optional[int] = None,
        edit_type: Literal["interaction", "message"] = "message",
        content: Optional[str] = MISSING,
        embed: Optional[Embed] = MISSING,
        embeds: Sequence[Embed] = MISSING,
        attachments: Sequence[Union[discord.Attachment, discord.File]] = MISSING,
        suppress: bool = False,
        delete_after: Optional[float] = None,
        allowed_mentions: Optional[discord.AllowedMentions] = MISSING,
        view: Optional[View] = MISSING,
        view_factory: Optional[Callable[..., Any]] = MISSING,
    ) -> None:
        if embed and embeds:
            raise ValueError(
                "Both embed and embeds were provided, but only one or neither should be provided."
            )
        if view and view_factory:
            raise ValueError(
                "Both view and view_factory were provided, but only one or neither should be provided."
            )

        self._edit_type = edit_type
        self._content = content
        self._embed = embed
        self._embeds = embeds
        self._attachments = attachments
        self._suppress = suppress
        self._delete_after = delete_after
        self._allowed_mentions = allowed_mentions
        self._new_view = view
        self._view_factory = view_factory
        custom_id = custom_id or f"{self.__class__.__name__}:{uuid4()}"

        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            emoji=emoji,
            row=row,
        )

    def _get_view(self) -> Optional[View]:
        # view_factory is used when we need to "lazy load" a view
        # This prevents us running into any recursion errors
        if self._new_view:
            return self._new_view
        if self._view_factory:
            return self._view_factory()
        if self._new_view == None or self._view_factory == None:
            return None
        return MISSING

    def _get_embed_kwarg(self) -> Dict[str, Any]:
        if self._embed:
            return {"embed": self._embed}
        elif self._embeds:
            return {"embeds": self._embeds}
        else:
            return {}

    async def callback(self, itr: discord.Interaction[ExultBot]) -> None:
        try:
            await itr.response.defer(ephemeral=True)
            view = self._get_view()
            embed_kwarg = self._get_embed_kwarg()

            if self.view:
                self.view.edited = True

            if self._edit_type == "message":
                if itr.message:
                    await itr.message.edit(
                        content=self._content,
                        attachments=self._attachments,
                        suppress=self._suppress,
                        delete_after=self._delete_after,
                        allowed_mentions=self._allowed_mentions,
                        view=view,
                        **embed_kwarg,
                    )
            else:
                await itr.edit_original_response(
                    content=self._content,
                    attachments=self._attachments,
                    allowed_mentions=self._allowed_mentions,
                    view=view,
                    **embed_kwarg,
                )
        except Exception as e:
            print(f"[CALLBACK_ERROR]: {type(e)}: ", e)


class DeleteMessage(Button[V], Generic[V]):
    """
    Builds on :class:`helpers.ui.Button` to easily generate a button that
    deletes the message the button is attached to.
    """

    view: V

    async def callback(self, itr: discord.Interaction[ExultBot]) -> None:
        await itr.response.defer(ephemeral=True)
        if itr.message:
            return await itr.message.delete()
        await itr.delete_original_response()


class ModalButton(ui.Button[V], Generic[V]):
    def __init__(
        self,
        modal: Callable[..., Any],
        *,
        style: ButtonStyle = ButtonStyle.secondary,
        label: str | None = None,
        disabled: bool = False,
        custom_id: str | None = None,
        url: str | None = None,
        emoji: str | Emoji | PartialEmoji | None = None,
        row: int | None = None,
    ) -> None:
        self.modal = modal
        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            url=url,
            emoji=emoji,
            row=row,
        )

    """
    Builds on :class:`helpers.ui.Button` to easily generate a button that
    returns a :class:`helpers.ui.Modal` instance to the user.
    """

    view: V

    async def callback(self, itr: discord.Interaction[ExultBot]) -> None:
        try:
            return await itr.response.send_modal(self.modal())
        except:
            traceback.print_exc()
