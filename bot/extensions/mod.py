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

from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from bot.utils.constants import EMBED_COLOR, LOG_CHANNEL_ID


class Mod(commands.Cog):
    """Comandos relacionados à moderação do servidor."""

    reasons = Literal[
        "Violação dos Diretrizes do Discord",
        "Divulgação de conteúdos sem autorização prévia",
        "Spamming, flooding ou qualquer outra forma de abuso",
        "Má convivência ou comportamento inapropriado",
        "Apelidos ou nomes de usuário inapropriados",
        "Desrespeitar o escopo dos canais ou servidor",
        "Burlamento de qualquer tipo de punição",
        "Mídias ou conteúdos inapropriados",
    ]

    punishments_mapping = {
        "kick": "Membro expulso",
        "ban": "Membro banido",
    }

    def __init__(self, bot):
        self.bot = bot

    @discord.utils.cached_property
    def log_channel(self):
        return self.bot.get_channel(LOG_CHANNEL_ID)

    def get_reason_message(self, ctx, reason):
        return (
            f"Ação executada por {ctx.author} (ID: {ctx.author.id}) | "
            f"Motivo: {reason}"
        )

    async def log(self, ctx, member, reason):
        """Logs an action to the log channel.

        Parameters
        ----------
        ctx: :class:`bot.utils.context.ThirteenContext`
            The context of the command.
        member: :class:`discord.Member`
            The member that was punished.
        reason: :class:`str`
            The reason of the punishment.
        """
        author = ctx.author
        title = self.punishments_mapping[ctx.command.name]

        embed = discord.Embed(title=title, color=EMBED_COLOR)
        embed.set_author(name=str(author), icon_url=author.display_avatar.url)
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="Usuário punido", value=str(member), inline=False)
        embed.add_field(name="ID", value=f"`{member.id}`", inline=False)
        embed.add_field(name="Motivo", value=reason, inline=False)

        await self.log_channel.send(embed=embed)

    @commands.hybrid_command()
    @commands.has_permissions(kick_members=True)
    @app_commands.default_permissions(kick_members=True)
    @app_commands.describe(member="Usuário a ser expulso.")
    @app_commands.describe(reason="Motivo da punição.")
    async def kick(self, ctx, member: discord.Member, reason: reasons):
        """Expulsa um usuário do servidor."""
        await member.kick(reason=self.get_reason_message(ctx, reason))
        await ctx.reply(f"**{member}** foi expulso do servidor.")

        await self.log(ctx, member, reason)

    @commands.hybrid_command()
    @commands.has_permissions(ban_members=True)
    @app_commands.default_permissions(ban_members=True)
    @app_commands.describe(member="Usuário a ser expulso.")
    @app_commands.describe(reason="Motivo da punição.")
    async def ban(self, ctx, member: discord.Member, reason: reasons):
        """Bane um usuário do servidor."""
        await member.ban(reason=self.get_reason_message(ctx, reason))
        await ctx.reply(f"**{member}** foi banido do servidor.")

        await self.log(ctx, member, reason)


async def setup(bot):
    await bot.add_cog(Mod(bot))
