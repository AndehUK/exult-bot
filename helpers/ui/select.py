from __future__ import annotations

# Core Imports
from uuid import uuid4
from typing import Generic, List, Optional

# Third Party Packages
import discord
from discord import ui

# Local Imports
from .views import V

__all__ = ("Select", "ChannelSelect", "UserSelect", "RoleSelect", "MentionableSelect")


class Select(ui.Select[V], Generic[V]):
    """
    Represents a UI select menu with a list of custom options.
    This is represented to the user as a dropdown menu.
    """

    view: V

    def __init__(
        self,
        *,
        custom_id: Optional[str] = None,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        options: List[discord.SelectOption] = discord.utils.MISSING,
        disabled: bool = False,
        row: Optional[int] = None,
    ) -> None:
        custom_id = custom_id or f"{self.__class__.__name__}:{uuid4()}"

        super().__init__(
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            options=options,
            disabled=disabled,
            row=row,
        )


class ChannelSelect(ui.ChannelSelect[V], Generic[V]):
    """
    Represents a UI select menu with a list of predefined options with
    the current channels in the guild.
    """

    view: V

    def __init__(
        self,
        *,
        custom_id: Optional[str] = None,
        channel_types: List[discord.ChannelType] = [],
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        row: Optional[int] = None,
    ) -> None:
        custom_id = custom_id or f"{self.__class__.__name__}:{uuid4()}"

        super().__init__(
            custom_id=custom_id,
            channel_types=channel_types,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
            row=row,
        )


class UserSelect(ui.UserSelect[V], Generic[V]):
    """
    Represents a UI select menu with a list of predefined options with
    the current members in the guild.
    """

    view: V

    def __init__(
        self,
        *,
        custom_id: Optional[str] = None,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        row: Optional[int] = None,
    ) -> None:
        custom_id = custom_id or f"{self.__class__.__name__}:{uuid4()}"

        super().__init__(
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
            row=row,
        )


class RoleSelect(ui.RoleSelect[V], Generic[V]):
    """
    Represents a UI select menu with a list of predefined options with
    the current roles in the guild.
    """

    view: V

    def __init__(
        self,
        *,
        custom_id: Optional[str] = None,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        row: Optional[int] = None,
    ) -> None:
        custom_id = custom_id or f"{self.__class__.__name__}:{uuid4()}"

        super().__init__(
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
            row=row,
        )


class MentionableSelect(ui.MentionableSelect[V], Generic[V]):
    """
    Represents a UI select menu with a list of predefined options with
    the current members and roles in the guild.
    """

    view: V

    def __init__(
        self,
        *,
        custom_id: Optional[str] = None,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        row: Optional[int] = None,
    ) -> None:
        custom_id = custom_id or f"{self.__class__.__name__}:{uuid4()}"

        super().__init__(
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
            row=row,
        )
