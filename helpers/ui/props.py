from typing import Dict

from discord import ButtonStyle


STATUS_LABEL: Dict[bool, str] = {True: "Disable", False: "Enable"}

STATUS_STYLE: Dict[bool, ButtonStyle] = {
    True: ButtonStyle.green,
    False: ButtonStyle.red,
}

COMPLETED_STYLE: Dict[bool, ButtonStyle] = {
    True: ButtonStyle.green,
    False: ButtonStyle.gray,
}
