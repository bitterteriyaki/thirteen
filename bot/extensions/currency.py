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

import random
from typing import Optional

from discord import Member, app_commands
from discord.app_commands import Range
from discord.ext import commands
from discord.ext.commands import Author, BucketType
from humanize import intcomma
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from bot.utils.database import CurrencyUser


class Currency(commands.Cog):
    """Comandos relacionados ao sistema de economia."""

    emoji = "\U0001fa99"

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        async with self.bot.db.connect() as conn:
            users = await conn.execute(select(CurrencyUser))

        for user_id, balance in users.all():
            await self.bot.cache.setnx(f"currency:{user_id}:balance", balance)

    async def add_credits(self, user_id, amount):
        """Adds credits to an user. If the user doesn't exist in the
        database, they will be inserted.

        Parameters
        ----------
        user_id: :class:`int`
            The user's ID.
        amount: :class:`int`
            The amount of credits to add.
        """
        async with self.bot.db.connect() as conn:
            insert_stmt = insert(CurrencyUser).values(id=user_id)
            stmt = insert_stmt.on_conflict_do_nothing()

            await conn.execute(stmt)
            await conn.execute(
                update(CurrencyUser)
                .where(CurrencyUser.id == user_id)
                .values(balance=CurrencyUser.balance + amount)
            )
            await conn.commit()

        await self.bot.cache.incrby(f"currency:{user_id}:balance", amount)

    async def remove_credits(self, user_id, amount):
        """Removes credits from an user. If the user doesn't exist in
        the database, nothing will happen.

        Parameters
        ----------
        user_id: :class:`int`
            The user's ID.
        amount: :class:`int`
            The amount of credits to remove.
        """
        async with self.bot.db.connect() as conn:
            await conn.execute(
                update(CurrencyUser)
                .where(CurrencyUser.id == user_id)
                .values(balance=CurrencyUser.balance - amount)
            )
            await conn.commit()

        await self.bot.cache.decrby(f"currency:{user_id}:balance", amount)

    async def set_credits(self, user_id, amount):
        """Sets credits to an user. If the user doesn't exist in the
        database, they will be inserted.

        Parameters
        ----------
        user_id: :class:`int`
            The user's ID.
        amount: :class:`int`
            The amount of credits to set.
        """
        async with self.bot.db.connect() as conn:
            insert_stmt = insert(CurrencyUser).values(id=user_id)
            stmt = insert_stmt.on_conflict_do_nothing()

            await conn.execute(stmt)
            await conn.execute(
                update(CurrencyUser)
                .where(CurrencyUser.id == user_id)
                .values(balance=amount)
            )
            await conn.commit()

        await self.bot.cache.set(f"currency:{user_id}:balance", amount)

    @commands.hybrid_command()
    @commands.cooldown(1, 86400, BucketType.user)
    @app_commands.describe(member="Usuário a quem dar os créditos.")
    async def daily(self, ctx, member: Member = Author):
        """Colete seus créditos diários (ou os dê para outro membro)."""
        amount = random.randint(25, 50)
        await self.add_credits(member.id, amount)

        await ctx.reply(f"{member.mention} recebeu **{amount} {self.emoji}**.")

    @commands.hybrid_command()
    @app_commands.describe(member="Usuário a quem transferir os créditos.")
    async def transfer(self, ctx, member: Member, amount: Range[int, 0, None]):
        """Transfira créditos para outro usuário."""
        if member.bot:
            return await ctx.reply(
                "Você não pode transferir créditos para bots."
            )

        if member == ctx.author:
            return await ctx.reply(
                "Você não pode transferir créditos para si mesmo."
            )

        balance = await ctx.cache.get(f"currency:{ctx.author.id}:balance") or 0

        if amount > balance:
            return await ctx.reply(
                "Você não tem créditos suficientes para fazer isso."
            )

        await self.remove_credits(ctx.author.id, amount)
        await self.add_credits(member.id, amount)

        message = (
            f"{ctx.author.mention} transferiu **{amount} {self.emoji}** para "
            f"{member.mention}."
        )
        await ctx.reply(message)

    @commands.hybrid_group(fallback="show")
    @app_commands.describe(member="Usuário para verificar o saldo.")
    async def balance(self, ctx, member: Member = Author):
        """Verifique seu saldo de créditos."""
        balance = await ctx.cache.get(f"currency:{member.id}:balance") or 0
        await ctx.reply(f"{member.mention} tem **{balance} {self.emoji}**.")

    @balance.command(name="add")
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(member="Usuário a receber os créditos.")
    @app_commands.describe(amount="Quantidade de créditos a ser adicionada.")
    async def balance_add(
        self,
        ctx,
        member: Optional[Member] = Author,
        *,
        amount: int,
    ):
        """Adicione créditos a um membro."""
        await self.add_credits(member.id, amount)

        message = (
            f"Adicionei **{intcomma(amount)} {self.emoji}** "
            f"a {member.mention}."
        )
        await ctx.reply(message)

    @balance.command(name="remove")
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(member="Usuário a perder os créditos.")
    @app_commands.describe(amount="Quantidade de créditos a ser removida.")
    async def balance_remove(
        self,
        ctx,
        member: Optional[Member] = Author,
        *,
        amount: int,
    ):
        """Remove créditos de um membro."""
        await self.remove_credits(member.id, amount)

        message = (
            f"Removi **{intcomma(amount)} {self.emoji}** de créditos "
            f"de {member.mention}."
        )
        await ctx.reply(message)

    @balance.command(name="set")
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(member="Usuário a ter os créditos definidos.")
    @app_commands.describe(amount="Quantidade de créditos a ser definida.")
    async def balance_set(
        self,
        ctx,
        member: Optional[Member] = Author,
        *,
        amount: int,
    ):
        """Defina os créditos de um membro."""
        await self.set_credits(member.id, amount)

        message = (
            f"Defini os créditos de {member.mention} para "
            f"**{intcomma(amount)} {self.emoji}**."
        )
        await ctx.reply(message)


async def setup(bot):
    await bot.add_cog(Currency(bot))
