from __future__ import annotations

from uuid import uuid4
from typing import Generic, List, Optional

import discord
from discord import ui

from .views import V


class Select(ui.Select[V], Generic[V]):
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
