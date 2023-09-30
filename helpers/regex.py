import re

from functools import cached_property


class RegEx:
    @cached_property
    def url_regex(self) -> re.Pattern[str]:
        return re.compile(
            r"^https?://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

    @cached_property
    def emoji_regex(self) -> re.Pattern[str]:
        return re.compile(
            r"<(a?):([a-zA-Z0-9\_]{1,32}):([0-9]{15,20})>$", re.IGNORECASE
        )
