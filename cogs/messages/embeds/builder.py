from discord import TextChannel

from helpers.colour import Colours
from helpers.embed import Embed

__all__ = ("MessageManagerEmbed", "MessageBuilderEmbed")


MessageManagerEmbed = Embed(
    title="Message Manager",
    description="Use the buttons below to manage your custom reusable messages!",
    colour=Colours.blue,
    fields=[
        {
            "name": "➕ Create Message",
            "value": "Create a new, custom reusable message!",
            "inline": True,
        },
        {
            "name": "🛠️ Edit Message",
            "value": "Edit one of your saved reusable messages!",
            "inline": True,
        },
        {
            "name": "🗑️ Delete Message(s)",
            "value": "Delete one or more of your saved reusable messages!",
            "inline": True,
        },
        {
            "name": "👁️ View Message",
            "value": "View one of your saved reusable messages!",
            "inline": True,
        },
        {
            "name": "🌐 Web Dashboard",
            "value": "Manage your messages on our web dashboard instead!",
            "inline": True,
        },
    ],
)


MessageBuilderEmbed = Embed(
    title="Message Builder",
    description="Use the buttons below to build your message!",
    colour=Colours.blue,
    fields=[
        {
            "name": "📃 Message Content",
            "value": "The plain text outside of embeds in your message.",
            "inline": True,
        },
        {
            "name": "📰 Embeds",
            "value": "Build your own embeds for your message.",
            "inline": True,
        },
        {
            "name": "📎 Import JSON",
            "value": (
                "Have an existing message you want to start with? Use our Context "
                "Menu command `Message Source` on your desired message and import "
                "the JSON data provided!"
            ),
            "inline": False,
        },
        {
            "name": "💨 Send and Exit",
            "value": (
                "Save your message for later, you can send it at a later date using "
                "the `/message send` command!"
            ),
            "inline": False,
        },
        {
            "name": "💌 Send and Send",
            "value": (
                "Send your message to your desired channel now and save it for later use as well!"
            ),
            "inline": False,
        },
        {
            "name": "📨 Send without Saving",
            "value": "Send your message to your desired channel now without saving it for later.",
            "inline": False,
        },
    ],
)

class SuccessEmbed(Embed):
    def __init__(self, channel: TextChannel)