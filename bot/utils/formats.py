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

from math import floor, log

__all__ = ("human_format", "progress_bar")


def human_format(number, units=["", "K", "M", "B", "T", "Q"]):
    """Formats a number to a human readable format. For example, `1.000`
    becomes `1.00K`, `1.000.000` becomes `1.00M`, and so on.

    Parameters
    ----------
    number: :class:`int`
        The number to format.
    units: :class:`list[:class:`str`]
        The units to use. Defaults to `["", "K", "M", "B", "T", "Q"]`.
    """
    if number < 1000:
        return str(number)

    base = 1000.0
    magnitude = int(floor(log(number, base)))
    return f"{number / base ** magnitude:.2f}{units[magnitude]}"


def progress_bar(amount, length=20, filled="█", empty="∙"):
    """Draw a progress bar. The progress bar is drawn using the `filled`
    and `empty` characters.

    Parameters
    ----------
    amount: :class:`int`
        The amount of progress. This should be a number between 0 and
        100.
    length: :class:`int`
        The length of the progress bar. Defaults to 20.
    filled: :class:`str`
        The character to use for the filled part of the progress bar.
        Defaults to `█`.
    empty: :class:`str`
        The character to use for the empty part of the progress bar.
        Defaults to `∙`.

    Returns
    -------
    :class:`str`
        A string containing the progress bar.
    """
    return f"{filled * round(int(amount) / (100 / length)):{empty}<{length}}"
