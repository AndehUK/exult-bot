from __future__ import annotations

from typing import List, Optional, TypeVar, TYPE_CHECKING, Union

from discord import Interaction, Message, ui


if TYPE_CHECKING:
    from bot import ExultBot
    from .buttons import Button
    from .modals import TextInput
    from .select import Select


__all__ = ("View", "V")

V = TypeVar("V", bound="View", covariant=True)


class View(ui.View):
    edited: bool
    message: Optional[Message]

    def __init__(
        self,
        itr: Optional[Interaction[ExultBot]] = None,
        *,
        timeout: Optional[float] = 600.0,
        personal: bool = False,
    ) -> None:
        self.itr = itr
        self.edited = False
        self.personal = personal

        super().__init__(timeout=timeout)

        self.children: List[Union[Button[View], Select[View], TextInput[View]]]

    def disable_view(self) -> None:
        for child in self.children:
            if isinstance(child, (Button, Select)):
                child.disabled = True

    async def interaction_check(self, itr: Interaction) -> bool:
        if self.personal and self.itr:
            if itr.user.id != self.itr.user.id:
                await itr.response.send_message(
                    f"Sorry! This menu belongs to {self.itr.user.mention}!",
                    ephemeral=True,
                )
                return False
        return True

    async def on_timeout(self) -> None:
        try:
            if not self.edited:
                self.disable_view()
                if self.message:
                    await self.message.edit(
                        content="Message components timed out.", view=self
                    )
        except:
            pass
