from typing import Dict

from discord import ButtonStyle

__all__ = ("COMPLETED_STYLE", "STATUS_LABEL", "STATUS_STYLE")


STATUS_LABEL: Dict[bool, str] = {True: "Disable", False: "Enable"}

STATUS_STYLE: Dict[bool, ButtonStyle] = {
    True: ButtonStyle.green,
    False: ButtonStyle.red,
}

COMPLETED_STYLE: Dict[bool, ButtonStyle] = {
    True: ButtonStyle.green,
    False: ButtonStyle.gray,
}
