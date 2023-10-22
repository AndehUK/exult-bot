# Core Imports
from uuid import uuid4
from typing import Generic, List, Optional

# Third Party Packages
import discord
from discord import ui

# Local Imports
from .views import V, View

__all__ = ("Modal", "TextInput")


class TextInput(ui.TextInput[V], Generic[V]):
    """Represents a UI text input."""

    def __init__(
        self,
        *,
        label: str,
        style: discord.TextStyle = discord.TextStyle.short,
        custom_id: Optional[str] = None,
        placeholder: Optional[str] = None,
        default: Optional[str] = None,
        required: bool = True,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        row: Optional[int] = None,
    ) -> None:
        custom_id = custom_id or f"{self.__class__.__name__}:{uuid4()}"

        super().__init__(
            label=label,
            style=style,
            custom_id=custom_id,
            placeholder=placeholder,
            default=default,
            required=required,
            min_length=min_length,
            max_length=max_length,
            row=row,
        )

        self.value: str


class Modal(ui.Modal):
    """Represents a UI modal."""

    def __init__(
        self,
        *,
        title: str,
        timeout: float = 600.0,
        custom_id: Optional[str] = None,
    ) -> None:
        custom_id = custom_id or f"{self.__class__.__name__}:{uuid4()}"

        super().__init__(
            title=title,
            timeout=timeout,
            custom_id=custom_id,
        )

        self.children: List[TextInput[View]]
