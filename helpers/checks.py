from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import ExultBot


VALID_IMAGE_CONTENT_TYPES = (
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/gif",
    "image/webp",
)


async def is_image_valid(bot: ExultBot, url: str) -> bool:
    try:
        async with bot.session.head(url) as r:
            content = r.headers.get("content-type")
            return content in VALID_IMAGE_CONTENT_TYPES
    except:
        pass
    return False
