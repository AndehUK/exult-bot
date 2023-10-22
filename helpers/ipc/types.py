# Core Imports
from typing import List, Optional, TypedDict


class MinimalDiscordCategory(TypedDict):
    id: int
    name: str


class MinimalDiscordChannel(TypedDict):
    category: Optional[MinimalDiscordCategory]
    id: int
    name: str
    type: int


class MinimalDiscordRole(TypedDict):
    colour: int
    name: str
    id: int


class MinimalDiscordGuild(TypedDict):
    channels: List[MinimalDiscordChannel]
    emojis: List[str]
    icon: Optional[str]
    id: int
    name: str
    owner_id: Optional[int]
    premium_tier: int
    roles: List[MinimalDiscordRole]
    unavailable: bool


class MinimalDiscordUser(TypedDict, total=False):
    username: str
    id: int
    avatar: str
    global_name: Optional[str]
    guilds: List[MinimalDiscordGuild]
