from __future__ import annotations

from typing import List, Optional, TypeVar, TYPE_CHECKING, Union

from discord import Interaction, Message, ui


if TYPE_CHECKING:
    from bot import ExultBot
    from .buttons import Button
    from .modals import TextInput
    from .select import Select


V = TypeVar("V", bound="View", covariant=True)


class View(ui.View):
    edited: bool
    message: Optional[Message]

    def __init__(
        self,
        ctx: Optional[Interaction[ExultBot]] = None,
        *,
        timeout: Optional[float] = 600.0,
        personal: bool = False,
    ) -> None:
        self.ctx = ctx
        self.edited = False
        self.personal = personal

        super().__init__(timeout=timeout)

        self.children: List[Union[Button[View], Select[View], TextInput[View]]]

    def disable_view(self) -> None:
        for child in self.children:
            if isinstance(child, (Button, Select)):
                child.disabled = True
