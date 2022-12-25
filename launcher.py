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

import click
import humanize

from bot.core import Thirteen


def run_bot():
    # active the `pt_BR` locale
    humanize.i18n.activate("pt_BR")
    # this following pull request was merged, but it's not released yet:
    # https://github.com/python-humanize/humanize/pull/66
    # so we need to set the decimal and thousand separators manually
    humanize.i18n._DECIMAL_SEPARATOR["pt_BR"] = ","
    humanize.i18n._THOUSANDS_SEPARATOR["pt_BR"] = "."

    bot = Thirteen()
    token = os.environ["TOKEN"]

    bot.run(token)


@click.group(invoke_without_command=True, options_metavar="[options]")
@click.pass_context
def main(ctx):
    """The main command group."""
    if ctx.invoked_subcommand is None:
        run_bot()


if __name__ == "__main__":
    main()
