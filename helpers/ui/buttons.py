from __future__ import annotations

from uuid import uuid4
from typing import Any, Generic, Literal, Optional, TypeVar, TYPE_CHECKING, Union

import discord
from discord import ui

from .views import View

if TYPE_CHECKING:
    from bot import ExultBot

__all__ = ("Button", "GoToButton", "URLButton", "DeleteMessage")


V = TypeVar("V", bound="View", covariant=True)


class Button(ui.Button[V], Generic[V]):
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
    view: V

    def __init__(self, label: str, url: str, row: Optional[int] = None) -> None:
        super().__init__(style=discord.ButtonStyle.url, label=label, url=url, row=row)


class GoToButton(Button[V], Generic[V]):
    view: V
    edit_type: Literal["interaction", "message"]

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
        **kwargs: Any,
    ) -> None:
        self.edit_type = edit_type
        self.kwargs = kwargs
        custom_id = custom_id or f"{self.__class__.__name__}:{uuid4()}"

        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            emoji=emoji,
            row=row,
        )

    async def callback(self, itr: discord.Interaction[ExultBot]) -> None:
        await itr.response.defer(ephemeral=True)
        if self.edit_type == "message":
            if itr.message:
                await itr.message.edit(**self.kwargs)
                if self.view:
                    self.view.edited = True
        else:
            await itr.edit_original_response(**self.kwargs)
            if self.view:
                self.view.edited = True


class DeleteMessage(Button[V], Generic[V]):
    view: V

    async def callback(self, itr: discord.Interaction[ExultBot]) -> None:
        await itr.response.defer(ephemeral=True)
        if itr.message:
            return await itr.message.delete()
        await itr.delete_original_response()
