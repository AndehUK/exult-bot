import asyncio
import os
from typing import Tuple

import click
import dotenv

from bot import ExultBot


@click.command()
@click.option("--sync", is_flag=True, help="Flag to trigger app command syncing")
@click.option(
    "--guilds",
    multiple=True,
    type=int,
    default=(-1,),
    show_default=True,
    help="Provide one or more guild IDs to sync app commands to. Default is -1 (Global commands).",
)
def cli(sync: bool, guilds: Tuple[int, ...]) -> None:
    asyncio.run(main(sync, guilds))


async def main(sync: bool, guilds: Tuple[int, ...]) -> None:
    dotenv.load_dotenv()

    bot = ExultBot(sync_on_ready=sync, guilds_to_sync=guilds)
    await bot.start(os.environ["BOT_TOKEN"])


if __name__ == "__main__":
    cli()
