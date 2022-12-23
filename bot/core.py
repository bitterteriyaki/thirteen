"""
Copyright (C) 2022-present  kyomi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import discord
from discord.ext import commands
from rich import print
from rich.table import Table
from rich.box import ROUNDED

from bot.utils.extensions import get_extensions
from bot.utils.context import ThirteenContext
from bot.utils.database import create_engine
from bot.utils.cache import create_cache


class Thirteen(commands.Bot):
    """The main bot class. This class inherits from
    :class:`discord.ext.commands.Bot` class.

    Attributes
    ----------
    is_first_run: :class:`bool`
        A boolean that indicates if the bot is running for the first
        time.
    db: :class:`sqlalchemy.ext.asyncio.AsyncEngine`
        The database connection engine.
    cache: :class:`redis.Redis`
        The Redis cache connection.
    """

    def __init__(self):
        intents = discord.Intents.none()
        intents.messages = True
        intents.message_content = True
        super().__init__(command_prefix=get_prefix, intents=intents)

        self.is_first_run = True
        self.db = create_engine()
        self.cache = create_cache()

    async def on_ready(self):
        if self.is_first_run:
            table = Table(
                title="✦ Bot is ready ✦",
                header_style="bold cyan",
                box=ROUNDED,
            )

            for column in ("ID", "Bot", "Users", "Commands"):
                table.add_column(column, justify="center")

            table.add_row(
                str(self.user.id),
                str(self.user),
                str(len(self.users)),
                str(len(self.tree.get_commands())),
            )
            print(table)

            self.is_first_run = False

    async def on_message(self, message):
        # ignore messages from bots and webhooks
        if not isinstance(message.author, discord.Member):
            return

        if message.author.bot:
            return

        self.dispatch("regular_message", message)
        await self.process_commands(message)

    async def setup_hook(self):
        for extension in get_extensions():
            await self.load_extension(extension)
            print(f"[green]✦ Loaded extension [u]{extension}[/][/]")

    async def get_context(self, message):
        return await super().get_context(message, cls=ThirteenContext)


async def get_prefix(bot, message):
    """Returns the prefix used for message commands.

    Parameters
    ---------
    bot: :class:`bot.core.Thirteen`
        The bot instance.
    message: :class:`discord.Message`
        The message that invoked the command.

    Returns
    -------
    :class:`str`
        The prefix used for message commands.

    Notes
    -----
    This command will be customizable in the future for user specific
    prefixes.
    """
    return "t!"
