from __future__ import annotations

# Core Imports
from typing import List, Optional, TypeVar, TYPE_CHECKING, Union

# Third Party Packages
from discord import Interaction, Message, ui

# Type Imports
if TYPE_CHECKING:
    from bot import ExultBot
    from .buttons import Button
    from .modals import TextInput
    from .select import Select


__all__ = ("View", "V")

V = TypeVar("V", bound="View", covariant=True)


class View(ui.View):
    """Represents a UI view."""

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
        """
        Disables all :class:`helpers.ui.Button` and :class:`helpers.ui.Select`
        instances attached to this view
        """

        for child in self.children:
            if isinstance(child, (Button, Select)):
                child.disabled = True

    async def interaction_check(self, itr: Interaction) -> bool:
        """
        A callback that is called when an interaction happens within the view
        that checks whether the view should process item callbacks for the interaction.
        """

        if self.personal and self.itr:
            if itr.user.id != self.itr.user.id:
                await itr.response.send_message(
                    f"Sorry! This menu belongs to {self.itr.user.mention}!",
                    ephemeral=True,
                )
                return False
        return True

    async def on_timeout(self) -> None:
        """
        A callback that is called when a view's timeout elapses without being explicitly stopped.
        """

        try:
            if not self.edited:
                self.disable_view()
                if self.message:
                    await self.message.edit(
                        content="Message components timed out.", view=self
                    )
        except:
            pass
