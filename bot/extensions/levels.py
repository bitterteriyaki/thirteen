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

from discord import Embed, Member, app_commands
from discord.ext import commands
from discord.ext.commands import Author, BucketType, CooldownMapping
from humanize import intcomma
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from bot.utils.constants import EMBED_COLOR
from bot.utils.database import LevelUser
from bot.utils.formats import human_format, progress_bar


class Levels(commands.Cog):
    """Comandos relacionados ao sistema de níveis."""

    def __init__(self, bot):
        self.bot = bot
        # users can only get experience two times per minute
        # this avoids users from spamming messages to get experience
        self.cooldown = CooldownMapping.from_cooldown(2, 60, BucketType.user)

    def get_level_exp(self, level):
        return 5 * (level**2) + 50 * level + 100

    def get_level_from_exp(self, exp):
        level = 0

        while exp >= self.get_level_exp(level):
            exp -= self.get_level_exp(level)
            level += 1

        return level

    async def cog_load(self):
        async with self.bot.db.connect() as conn:
            users = await conn.execute(select(LevelUser))

        for user_id, exp in users.all():
            await self.bot.cache.setnx(f"levels:{user_id}:experience", exp)

    async def add_experience(self, user_id, value):
        """Adds experience to an user. If the user doesn't exist in the
        database, it will be created.

        Parameters
        ----------
        user_id: :class:`int`
            The user ID.
        value: :class:`int`
            The amount of experience to add.
        """
        async with self.bot.db.connect() as conn:
            insert_stmt = insert(LevelUser).values(id=user_id)
            stmt = insert_stmt.on_conflict_do_nothing()

            await conn.execute(stmt)
            await conn.commit()

        async with self.bot.db.connect() as conn:
            await conn.execute(
                update(LevelUser)
                .where(LevelUser.id == user_id)
                .values(experience=LevelUser.experience + value)
            )
            await conn.commit()

        await self.bot.cache.incrby(f"levels:{user_id}:experience", value)

    async def remove_experience(self, user_id, value):
        """Removes experience to an user. If the user doesn't exist in
        the database, nothing will happen. If the value is greater than
        the user's experience, it will be clamped to 0.

        Parameters
        ----------
        user_id: :class:`int`
            The user ID.
        value: :class:`int`
            The amount of experience to add.
        """
        async with self.bot.db.connect() as conn:
            stmt = select(LevelUser).where(LevelUser.id == user_id)
            user = (await conn.execute(stmt)).first()

            if user is None:
                return

            value = min(value, user.experience)

            await conn.execute(
                update(LevelUser)
                .where(LevelUser.id == user_id)
                .values(experience=LevelUser.experience - value)
            )
            await conn.commit()

        await self.bot.cache.decrby(f"levels:{user_id}:experience", value)

    async def set_experience(self, user_id, value):
        """Sets experience to an user. If the user doesn't exist in the
        database, it will be created.

        Parameters
        ----------
        user_id: :class:`int`
            The user ID.
        value: :class:`int`
            The amount of experience to add.
        """
        async with self.bot.db.connect() as conn:
            insert_stmt = insert(LevelUser).values(id=user_id)
            stmt = insert_stmt.on_conflict_do_nothing()

            await conn.execute(stmt)
            await conn.commit()

        async with self.bot.db.connect() as conn:
            await conn.execute(
                update(LevelUser)
                .where(LevelUser.id == user_id)
                .values(experience=value)
            )
            await conn.commit()

        await self.bot.cache.set(f"levels:{user_id}:experience", value)

    @commands.Cog.listener()
    async def on_regular_message(self, message):
        bucket = self.cooldown.get_bucket(message)
        retry_after = bucket.update_rate_limit()

        if retry_after:
            return

        author = message.author
        amount = random.randint(15, 25)

        exp = await self.bot.cache.get(f"levels:{author.id}:experience") or 0
        level = self.get_level_from_exp(exp)

        await self.add_experience(author.id, amount)
        new_level = self.get_level_from_exp(exp + amount)

        if new_level > level:
            avatar = author.display_avatar
            content = (
                f"Parabéns, {author.mention}! Você subiu para o "
                f"**nível {new_level}**!"
            )

            embed = Embed(description=content, color=EMBED_COLOR)
            embed.set_author(name=author.display_name, icon_url=avatar.url)
            await message.reply(embed=embed, mention_author=False)

    @commands.hybrid_group(fallback="profile")
    @app_commands.describe(member="Usuário a ser verificado.")
    async def exp(self, ctx, member: Member = Author):
        """Verifica a sua experiência ou a de um usuário."""
        exp = await self.bot.cache.get(f"levels:{member.id}:experience") or 0
        level = self.get_level_from_exp(exp)

        used_exp = exp - sum(self.get_level_exp(i) for i in range(level))
        percentage = (used_exp / self.get_level_exp(level)) * 100

        content = (
            f"Experiência: **{human_format(exp)}**\n"
            f"Nível: **{intcomma(level)}**\n\n"
            f"`{progress_bar(percentage)}`"
        )
        await ctx.reply(content)

    @exp.command(name="add")
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(member="Usuário a receber a experiência.")
    @app_commands.describe(
        amount="Quantidade de experiência a ser adicionada.",
    )
    async def exp_add(
        self,
        ctx,
        member: Optional[Member] = Author,
        *,
        amount: int,
    ):
        """Adiciona experiência a um usuário."""
        await self.add_experience(member.id, amount)

        message = (
            f"Adicionei `{intcomma(amount)}` de experiência "
            f"a {member.mention}."
        )
        await ctx.reply(message)

    @exp.command(name="remove")
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(member="Usuário a perder a experiência.")
    @app_commands.describe(amount="Quantidade de experiência a ser removida.")
    async def exp_remove(
        self,
        ctx,
        member: Optional[Member] = Author,
        *,
        amount: int,
    ):
        """Remove experiência de um usuário."""
        await self.remove_experience(member.id, amount)

        message = (
            f"Removi `{intcomma(amount)}` de experiência "
            f"de {member.mention}."
        )
        await ctx.reply(message)

    @exp.command(name="set")
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(member="Usuário a ter a experiência definida.")
    @app_commands.describe(amount="Quantidade de experiência a ser definida.")
    async def exp_set(
        self,
        ctx,
        member: Optional[Member] = Author,
        *,
        amount: int,
    ):
        """Define a experiência de um usuário."""
        await self.set_experience(member.id, amount)

        message = (
            f"Defini a experiência de {member.mention} "
            f"para `{intcomma(amount)}`."
        )
        await ctx.reply(message)


async def setup(bot):
    await bot.add_cog(Levels(bot))
