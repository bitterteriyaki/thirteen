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

import os

from sqlalchemy import Column, BigInteger
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine


Base = declarative_base()


def create_engine():
    """Creates the database engine. This function is used to connect
    with the database.

    Returns
    -------
    :class:`sqlalchemy.ext.asyncio.AsyncEngine`
        The database connection engine.
    """
    return create_async_engine(os.environ["DATABASE_URL"])


class LevelUser(Base):
    """A model representing a user in the levels system.

    Attributes
    ----------
    id: :class:`int`
        The user's ID.
    experience: :class:`int`
        The user's experience.
    """

    __tablename__ = "levels"

    id = Column(BigInteger, primary_key=True)
    experience = Column(BigInteger, default=0, nullable=False)
