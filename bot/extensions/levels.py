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

from discord import Embed
from discord.ext import commands
from discord.ext.commands import CooldownMapping, BucketType
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from bot.utils.database import LevelUser
from bot.utils.constants import EMBED_COLOR


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
        """Adds experience to a user. If the user doesn't exist in the
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


async def setup(bot):
    await bot.add_cog(Levels(bot))
