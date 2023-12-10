import typing

if typing.TYPE_CHECKING:
    from helpers.embed import Embed

__all__ = ("MessageBuilderData",)


class MessageBuilderData(typing.TypedDict):
    guild_id: int
    content: typing.Optional[str]
    embeds: typing.List[Embed]
    edit: typing.Optional[str]
