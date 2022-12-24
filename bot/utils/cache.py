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

import redis.asyncio as redis


def create_cache():
    """Create a Redis cache instance. This function is called in the
    the :class:`bot.core.Thirteen` class.

    Returns
    -------
    :class:`redis.Redis`
        A Redis cache instance.
    """

    def convert_to_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return value

    r = redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    r.set_response_callback("GET", convert_to_int)
    return r
