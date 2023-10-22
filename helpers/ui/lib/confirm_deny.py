from __future__ import annotations

# Core Imports
from typing import Optional, TYPE_CHECKING

# Third Party Packages
import discord

# Local Imports
from bot import ExultBot
from .. import Button, View

# Type Imports
if TYPE_CHECKING:
    from bot import ExultBot

__all__ = ("ConfirmDeny",)


class ConfirmDeny(View):
    """
    A simple :class:`helpers.ui.View` that allows the end-user to confirm or deny
    a choice they have made.

    With a default configuration the buttons return a boolean value, `True` on confirm,
    `False` on deny.

    The callbacks for these buttons can be modified by overwriting the :meth:`on_confirm`
    and :meth:`on_deny` methods respectively.
    """

    value: Optional[bool]

    def __init__(
        self,
        itr: Optional[discord.Interaction[ExultBot]] = None,
        *,
        timeout: Optional[float] = 600.0,
        personal: bool = False,
        return_value: bool = True,
        row: int = 0,
    ) -> None:
        self.return_value = return_value
        super().__init__(itr, timeout=timeout, personal=personal)

        confirm: Button[ConfirmDeny] = Button(
            style=discord.ButtonStyle.green, label="Confirm", emoji="✅", row=row
        )
        confirm.callback = self.on_confirm

        deny: Button[ConfirmDeny] = Button(
            style=discord.ButtonStyle.red, label="Deny", emoji="✖️", row=row
        )
        deny.callback = self.on_deny

        self.add_item(confirm)
        self.add_item(deny)

    async def on_confirm(self, interaction: discord.Interaction[ExultBot]) -> None:
        """
        Returns a `True` value if `self.return_value` is `True`.

        This method should be overwritten if additional functionality is required.
        """
        if self.return_value:
            await interaction.response.defer(ephemeral=True)
            self.value = True
            self.stop()

    async def on_deny(self, interaction: discord.Interaction[ExultBot]) -> None:
        """
        Returns a `False` value if `self.return_value` is `True`.

        This method should be overwritten if additional functionality is required.
        """
        if self.return_value:
            await interaction.response.defer(ephemeral=True)
            self.value = False
            self.stop()
