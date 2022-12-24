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

from discord.ext import commands


class Owner(commands.Cog):
    """Comandos exclusivos para o dono do bot."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.hybrid_command()
    async def sync(self, ctx):
        """Sincroniza os comandos do bot com o lado do Discord."""
        synced = await ctx.bot.tree.sync()
        message = f"Foram sincronizados `{len(synced)}` comandos."
        await ctx.reply(message)


async def setup(bot):
    await bot.add_cog(Owner(bot))
