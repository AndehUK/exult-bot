from __future__ import annotations

from typing import List, TYPE_CHECKING

import discord
from prisma.enums import AutoroleMode
from prisma.models import AutoroleConfig as Config

from helpers import ui
from helpers.colour import Colours
from helpers.embed import Embed

if TYPE_CHECKING:
    from helpers.types import ExultInteraction


__all__ = ("AutoroleConfig",)


class ViewFactory:
    @staticmethod
    def create_autorole_manager(
        ctx: ExultInteraction, config: Config, *, remove: bool = False
    ) -> ManageAutoroles:
        return ManageAutoroles(ctx, config, remove=remove)

    @staticmethod
    def create_autorole_config(ctx: ExultInteraction, config: Config) -> AutoroleConfig:
        return AutoroleConfig(ctx, config)


class ToggleAutoroles(ui.Button[ui.V]):
    def __init__(self, ctx: ExultInteraction, config: Config) -> None:
        self.ctx = ctx
        self.config = config
        super().__init__(
            style=ui.STATUS_STYLE[self.config.autorole_status],
            label=ui.STATUS_LABEL[self.config.autorole_status],
        )

    async def callback(self, itr: ExultInteraction) -> None:
        assert itr.guild
        await itr.response.defer(ephemeral=True)

        new_value = not self.config.autorole_status
        config = await itr.client.db.autoroleconfig.update(
            {"autorole_status": new_value},
            {"guild_id": itr.guild.id},
            {"autoroles": True},
        )

        if not config:
            return await itr.followup.send(
                "Something went wrong whilst updating the autoroles config. "
                "Please try again later.",
                ephemeral=True,
            )

        view = AutoroleConfig(itr, config)
        await itr.edit_original_response(view=view)
        self.view.edited = True


class ToggleMode(ui.Button[ui.V]):
    def __init__(self, ctx: ExultInteraction, config: Config) -> None:
        self.ctx = ctx
        self.config = config
        super().__init__(
            style=discord.ButtonStyle.blurple,
            label=f"Mode: {self.config.autorole_mode.replace('_', ' ').title()}",
        )

    async def callback(self, itr: ExultInteraction) -> None:
        assert itr.guild
        await itr.response.defer(ephemeral=True)

        new_value = (
            AutoroleMode.on_join
            if self.config.autorole_mode == AutoroleMode.on_verify
            else AutoroleMode.on_verify
        )
        config = await itr.client.db.autoroleconfig.update(
            {"autorole_mode": new_value},
            {"guild_id": itr.guild.id},
            {"autoroles": True},
        )

        if not config:
            return await itr.followup.send(
                "Something went wrong whilst updating the autoroles config. "
                "Please try again later.",
                ephemeral=True,
            )

        view = AutoroleConfig(itr, config)
        await itr.edit_original_response(view=view)
        self.view.edited = True


class AutoroleSelector(ui.RoleSelect[ui.V]):
    def __init__(
        self, ctx: ExultInteraction, config: Config, *, remove: bool = False
    ) -> None:
        assert ctx.guild

        self.ctx = ctx
        self.config = config
        self.remove = remove
        action = "add" if not remove else "remove"

        super().__init__(
            placeholder=f"Select a role to {action}!", max_values=len(ctx.guild.roles)
        )

    async def callback(self, itr: ExultInteraction) -> None:
        assert itr.guild and self.config.autoroles
        await itr.response.defer(ephemeral=True)

        embed = Embed(description=f"## Autoroles Config")

        if not self.remove:
            unassignable: List[discord.Role] = [
                r for r in self.values if not r.is_assignable()
            ]
            already_configured: List[discord.Role] = [
                r
                for r in [r for r in self.values if r not in unassignable]
                if r.id in [ar.role_id for ar in self.config.autoroles]
            ]
            adding = [r for r in self.values if r not in already_configured]

            try:
                await itr.client.db.autorole.create_many(
                    [{"guild_id": itr.guild.id, "role_id": r.id} for r in adding]
                )
            except Exception as e:
                roles = "\n".join([f"- {r.mention}" for r in adding])
                assert embed.description
                embed.description += f"\nFailed to add the following roles to the autoroles config:\n{roles}"
                embed.set_footer(text=f"{str(type(e)).title()}: {e}")
                embed.colour = Colours.red
                return await itr.followup.send(embed=embed, ephemeral=True)

            if len(adding):
                roles = "\n".join([f"- {r.mention}" for r in adding])
                embed.add_field(name="New Autoroles", value=roles)
            if len(unassignable):
                roles = "\n".join([f"- {r.mention}" for r in unassignable])
                embed.add_field(name="Unassignable by me", value=roles)
            if len(already_configured):
                roles = "\n".join([f"- {r.mention}" for r in already_configured])
                embed.add_field(name="Already Configured", value=roles)
            embed.colour = Colours.green
        else:
            # We're removing existing autoroles
            not_configured = [
                r
                for r in self.values
                if r.id not in [ar.role_id for ar in self.config.autoroles]
            ]
            deleted: List[discord.Role] = []
            failed: List[discord.Role] = []

            for r in [r for r in self.values if r not in not_configured]:
                try:
                    await itr.client.db.autorole.delete(
                        {
                            "guild_id_role_id": {
                                "guild_id": itr.guild.id,
                                "role_id": r.id,
                            }
                        }
                    )
                    deleted.append(r)
                except Exception as e:
                    failed.append(r)

            if len(deleted):
                roles = "\n".join([f"- {r.mention}" for r in deleted])
                embed.add_field(name="Deleted Autoroles", value=roles)
            if len(failed):
                roles = "\n".join([f"- {r.mention}" for r in failed])
                embed.add_field(name="Failed to Delete", value=roles)
            if len(not_configured):
                roles = "\n".join([f"- {r.mention}" for r in not_configured])
                embed.add_field(name="Not Configured", value=roles)
            embed.colour = Colours.red

        config = await itr.client.db.autoroleconfig.find_unique(
            {"guild_id": itr.guild.id}, {"autoroles": True}
        )
        if not config:
            return await itr.followup.send(
                "Something went wrong whilst updating the autoroles config. "
                "Please try again later.",
                ephemeral=True,
            )

        view = AutoroleConfig(itr, config)
        await itr.edit_original_response(view=view)
        self.view.edited = True
        await itr.followup.send(embed=embed, ephemeral=True)


class ManageAutoroles(ui.View):
    def __init__(
        self, ctx: ExultInteraction, config: Config, *, remove: bool = False
    ) -> None:
        super().__init__(ctx, personal=True)

        self.add_item(AutoroleSelector(ctx, config, remove=remove))
        self.add_item(
            ui.GoToButton(
                style=discord.ButtonStyle.red,
                label="Go Back",
                row=1,
                edit_type="message",
                view_factory=lambda: ViewFactory.create_autorole_config(ctx, config),
            )
        )
        self.add_item(ui.CANCEL_BUTTON_1)


class ViewAutoroles(ui.Button[ui.V]):
    def __init__(self, config: Config) -> None:
        self.config = config
        assert self.config.autoroles != None

        super().__init__(
            style=discord.ButtonStyle.gray,
            label=f"View Autoroles ({len(self.config.autoroles)})",
            disabled=len(self.config.autoroles) == 0,
        )

    async def callback(self, itr: ExultInteraction) -> None:
        assert itr.guild and self.config.autoroles
        await itr.response.defer(ephemeral=True)

        if not len(self.config.autoroles):
            return await itr.followup.send(
                "No autoroles have been configured for this server!", ephemeral=True
            )

        status = "Enabled" if self.config.autorole_status else "Disabled"
        mode = self.config.autorole_mode.replace("_", " ").title()
        roles = "\n".join([f"- <@&{r.role_id}>" for r in self.config.autoroles])
        embed = Embed(
            description=(
                f"## Autoroles\n**__Status:__** {status}\n"
                f"**__Mode:__** {mode}\n### Roles\n{roles}"
            ),
            colour=Colours.green,
        )
        await itr.followup.send(embed=embed, ephemeral=True)


class AutoroleConfig(ui.View):
    def __init__(self, ctx: ExultInteraction, config: Config) -> None:
        super().__init__(ctx, personal=True)

        self.add_item(ToggleAutoroles(ctx, config))
        self.add_item(ToggleMode(ctx, config))
        self.add_item(
            ui.GoToButton(
                style=discord.ButtonStyle.green,
                label="Add Autoroles",
                row=1,
                emoji="➕",
                edit_type="message",
                view_factory=lambda: ViewFactory.create_autorole_manager(
                    ctx, config, remove=False
                ),
            )
        )
        self.add_item(
            ui.GoToButton(
                style=discord.ButtonStyle.green,
                label="Remove Autoroles",
                row=1,
                emoji="➖",
                edit_type="message",
                view_factory=lambda: ViewFactory.create_autorole_manager(
                    ctx, config, remove=True
                ),
            )
        )
        self.add_item(ViewAutoroles(config))  # View Autoroles
        self.add_item(ui.CANCEL_BUTTON_1)
