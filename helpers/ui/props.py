# Core Imports
from typing import Dict

# Third Party Packages
from discord import ButtonStyle

__all__ = ("COMPLETED_STYLE", "STATUS_LABEL", "STATUS_STYLE")

# Helper dictionary that generates text based on a boolean value
STATUS_LABEL: Dict[bool, str] = {True: "Disable", False: "Enable"}

# Helper dictionary that generates a :class:`discord.ButtonStyle` based on a boolean value
STATUS_STYLE: Dict[bool, ButtonStyle] = {
    True: ButtonStyle.green,
    False: ButtonStyle.red,
}

# Helper dictionary that generates a :class:`discord.ButtonStyle` based on a boolean value
COMPLETED_STYLE: Dict[bool, ButtonStyle] = {
    True: ButtonStyle.green,
    False: ButtonStyle.gray,
}
