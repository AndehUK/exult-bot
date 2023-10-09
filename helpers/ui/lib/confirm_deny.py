from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import discord

from bot import ExultBot

from .. import Button, View

if TYPE_CHECKING:
    from bot import ExultBot

__all__ = ("ConfirmDeny",)


class ConfirmDeny(View):
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
        if self.return_value:
            await interaction.response.defer(ephemeral=True)
            self.value = True
            self.stop()

    async def on_deny(self, interaction: discord.Interaction[ExultBot]) -> None:
        if self.return_value:
            await interaction.response.defer(ephemeral=True)
            self.value = False
            self.stop()
