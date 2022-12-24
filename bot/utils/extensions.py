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

import re
import os


__all__ = ("get_extensions",)


def get_extensions(*, path="bot/extensions"):
    """Returns a list of all the extensions in the given path. The path
    is relative to the root directory of the bot.

    Parameters
    ----------
    path: :class:`str`
        The path to the extensions directory. Defaults to
        ``bot/extensions``.

    Returns
    -------
    List[:class:`str`]
        A list of all the extensions in the given path.
    """
    extensions = []

    for root, _, files in os.walk(path):
        for file in files:
            filename, ext = os.path.splitext(file)

            if ext != ".py":
                continue

            extension = re.sub(os.sep, ".", os.path.join(root, filename))
            extensions.append(extension)

    return extensions
