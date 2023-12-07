from __future__ import annotations

# Core Imports
import datetime
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Self,
    Tuple,
    TypedDict,
    TYPE_CHECKING,
    Sequence,
    Union,
)

# Third Party Packages
import discord
from prisma.models import Embed as DBEmbed

# Local Imports
from helpers.checks import is_image_valid
from helpers.colour import Colours

# Type Imports
if TYPE_CHECKING:
    from bot import ExultBot


class EmbedAuthor(TypedDict, total=False):
    icon_url: str
    name: str


class EmbedFooter(TypedDict, total=False):
    icon_url: str
    text: str


class EmbedField(TypedDict):
    name: str
    value: str
    inline: bool


class Embed(discord.Embed):
    """Subclass of :class:`discord.Embed` that provides some additional functionality"""

    def __init__(
        self,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        colour: Optional[Union[discord.Colour, int]] = None,
        timestamp: Optional[datetime.datetime] = None,
        author: Optional[EmbedAuthor] = None,
        footer: Optional[EmbedFooter] = None,
        thumbnail: Optional[str] = None,
        image: Optional[str] = None,
        fields: List[EmbedField] = [],
        url: Optional[str] = None,
        _id: Optional[int] = None,
    ) -> None:
        self._id = _id
        super().__init__(
            colour=colour,
            title=title,
            url=url,
            description=description,
            timestamp=timestamp,
        )
        if author:
            if "name" not in author:
                raise ValueError("missing author name")
            self.set_author(name=author["name"], icon_url=author.get("icon_url"))
        if footer:
            if "text" not in footer:
                raise ValueError("missing footer text")
            self.set_footer(text=footer["text"], icon_url=footer.get("icon_url"))
        self.set_thumbnail(url=thumbnail)
        self.set_image(url=image)
        for pos, field in enumerate(fields):
            if not field.get("name"):
                raise ValueError(f"missing name in field {pos}")
            elif not field.get("value"):
                raise ValueError(f"missing value in field {pos}")
            self.add_field(
                name=field["name"],
                value=field["value"],
                inline=field.get("inline", True),
            )

    def is_minimal_ready(self) -> bool:
        return any(
            (
                self.title,
                self.description,
                self.fields,
                self.timestamp,
                self.author,
                self.thumbnail,
                self.footer,
                self.image,
            )
        )

    def add_named_field(self, name: str, *, inline: bool = True) -> None:
        """Creates a new :class:`Embed` field with the provided name and an invisible value"""
        self.add_field(name=name, value="\u200b", inline=inline)

    def add_invisible_field(self, *, inline: bool = True) -> Embed:
        """Creates a new invisible :class:`Embed` field"""
        self.add_field(name="\u200b", value="\u200b", inline=inline)
        return self

    def to_discord_embed(self) -> discord.Embed:
        """Converts our custom :class:`Embed` instance to an actual :class:`discord.Embed`"""
        super().from_dict
        return discord.Embed.from_dict(self.to_dict())

    @classmethod
    def from_db(cls, data: DBEmbed) -> Self:
        """Converts a :class:`prisma.models.Embed` to a :class:`helpers.embed.Embed`"""
        # we are bypassing __init__ here since it doesn't apply here
        self = cls.__new__(cls)

        # fill in the basic fields

        self.title = data.title
        self.type = "rich"
        self.description = data.description
        self.url = data.url
        self._colour = discord.Colour(data.colour or Colours.embed_default)
        self._timestamp = data.timestamp
        self.set_image(url=data.image)
        self.set_thumbnail(url=data.thumbnail)

        # Try to fill in the more rich fields

        if data.author:
            self.set_author(
                name=data.author.name, icon_url=data.author.icon, url=data.author.url
            )
        if data.footer:
            self.set_footer(text=data.footer.text, icon_url=data.footer.icon)

        if data.fields:
            for field in data.fields:
                self.add_field(name=field.name, value=field.value, inline=field.inline)

        return self

    @classmethod
    async def from_user_dict(cls, bot: ExultBot, data: Dict[str, Any]) -> Self:
        """Tries to convert a user-provided :class:`dict` to a valid :class:`helpers.embed.Embed`"""

        # we are bypassing __init__ here since it doesn't apply here
        self = cls.__new__(cls)

        if "color" in data:
            try:
                colour = discord.Colour(data.get("color", None))
            except:
                raise ValueError("Invalid value given for key: `color`")
        elif "colour" in data:
            try:
                colour = discord.Colour(data.get("colour", None))
            except:
                raise ValueError("Invalid value given for key: `color`")
        else:
            colour = Colours.embed_default

        if "timestamp" in data:
            try:
                timestamp = datetime.datetime.fromisoformat(data["timestamp"])
            except Exception:
                raise ValueError(
                    "Invalid value given for key: `timestamp`. Value must be a valid timestamp."
                )
        else:
            timestamp = None

        if "thumbnail" in data:
            is_url = bot.regex.url_regex.search(data["thumbnail"])
            if not is_url:
                raise ValueError("Embed thumbnail must be a direct image url.")
            if not await is_image_valid(bot, data["thumbnail"]):
                raise ValueError("Embed thumbnail must be a direct image url.")
            thumbnail = data["thumbnail"]
        else:
            thumbnail = None

        if "image" in data:
            is_url = bot.regex.url_regex.search(data["image"])
            if not is_url:
                raise ValueError("Embed image must be a direct image url.")
            if not await is_image_valid(bot, data["image"]):
                raise ValueError("Embed image must be a direct image url.")
            image = data["image"]
        else:
            image = None

        author: Dict[str, str] = {}
        if "author" in data:
            if "name" not in data["author"] or len(str(data["author"]["name"])) > 256:
                raise ValueError(
                    "Embed Author name must exist and be equal to or less than "
                    "`256 characters` in length."
                )
            else:
                author["name"] = str(data["author"]["name"])
            if "icon_url" in data["author"]:
                is_url = bot.regex.url_regex.search(data["author"]["icon_url"])
                if not is_url:
                    raise ValueError(
                        "Embed Author icon url must be a direct image url."
                    )
                if not await is_image_valid(bot, data["author"]["icon_url"]):
                    raise ValueError(
                        "Embed Author icon url must be a direct image url."
                    )
                author["icon_url"] = data["author"]["icon_url"]
            if "url" in data["author"]:
                is_url = bot.regex.url_regex.search(data["author"]["url"])
                if not is_url:
                    raise ValueError("Embed Author url must be a valid url.")
                author["url"] = data["author"]["url"]

        footer: Dict[str, str] = {}
        if "footer" in data:
            if "text" not in data["footer"] or len(str(data["footer"]["text"])) > 2048:
                raise ValueError(
                    "Embed Footer text must exist and be equal to or less than "
                    "`2048 characters` in length."
                )
            else:
                footer["text"] = str(data["footer"]["text"])
            if "icon_url" in data["footer"]:
                is_url = bot.regex.url_regex.search(data["footer"]["icon_url"])
                if not is_url:
                    raise ValueError(
                        "Embed Footer icon url must be a direct image url."
                    )
                if not await is_image_valid(bot, data["footer"]["icon_url"]):
                    raise ValueError(
                        "Embed Footer icon url must be a direct image url."
                    )
                footer["icon_url"] = data["footer"]["icon_url"]

        self.type = "rich"
        self.title = data.get("title", None)
        self.description = data.get("description", None)
        self.url = data.get("url", None)

        if colour:
            self._colour = colour
        if timestamp:
            self._timestamp = timestamp
        if thumbnail:
            self._thumbnail = thumbnail
        if image:
            self._image = image

        if author:
            self._author = {
                "name": author["name"],
                "url": author.get("url", None),
                "icon_url": author.get("icon_url", None),
            }
        if footer:
            self._footer = {
                "text": footer["text"],
                "icon_url": footer.get("icon_url", None),
            }

        if "fields" in data:
            required: Tuple[str, ...] = ("name", "value")
            if not isinstance(data["fields"], Sequence):
                raise TypeError("Embed Fields must be an array.")
            fields: Sequence[Dict[str, Any]] = data["fields"]
            for pos, field in enumerate(fields):
                for req in required:
                    if req not in field:
                        raise ValueError(f"Missing property `{req}` in field `{pos}`")
                name = field.get("name", "")
                if not bool(name) or len(name) > 256:
                    raise ValueError(
                        f"Embed Field {pos} name must be between 1 and 256 characters in length."
                    )
                value = field.get("value", "")
                if not bool(value) or len(value) > 1024:
                    raise ValueError(
                        f"Embed Field {pos} value must be between 1 and 1024 characters in length."
                    )
                inline = field.get("inline", False)
                if not isinstance(inline, bool):
                    raise TypeError(f"Field {pos} inline must be a boolean type.")
                self.add_field(name=name, value=value, inline=inline)

        return self
