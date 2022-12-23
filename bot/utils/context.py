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

from discord import Embed
from discord.ext.commands import Context

from bot.utils.constants import EMBED_COLOR


class ThirteenContext(Context):
    """A custom context class that inherits from
    :class:`discord.ext.commands.Context` and adds some utility methods.
    """

    def get_embed(self, content):
        """This method is a factory method that creates an embed with
        the given content. The embed is created with the default color
        and the content is set as the description.

        Parameters
        ----------
        content: :class:`str`
            The content of the embed.

        Returns
        -------
        :class:`discord.Embed`
            A new embed with the given content.
        """
        author = self.author
        avatar = author.display_avatar

        embed = Embed(description=content, color=EMBED_COLOR)
        embed.set_author(name=author.display_name, icon_url=avatar.url)
        return embed

    async def reply(self, content):
        """This method is a wrapper for
        :meth:`dicord.ext.commands.Context.reply` that adds an embed to
        the message.

        Parameters
        ----------
        content: :class:`str`
            The content of the message.

        Returns
        -------
        :class:`discord.Message`
            The message that was sent.
        """
        embed = self.get_embed(content)
        return await super().reply(embed=embed, mention_author=False)
