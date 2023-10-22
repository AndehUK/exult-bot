from __future__ import annotations

# Core Imports
from typing import TYPE_CHECKING

# Type Imports
if TYPE_CHECKING:
    from bot import ExultBot


# Image types that we accept that our `is_image_valid` coroutine checks against
VALID_IMAGE_CONTENT_TYPES = (
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/gif",
    "image/webp",
)


async def is_image_valid(bot: ExultBot, url: str) -> bool:
    """
    Checks to see if the provided URL is a valid direct image URL
    """

    try:
        # Performs a HTTP head request to the given URL
        async with bot.session.head(url) as r:
            content = r.headers.get("content-type")
            return content in VALID_IMAGE_CONTENT_TYPES
    except:
        pass
    return False
