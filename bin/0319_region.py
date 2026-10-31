# SPDX-License-Identifier: GPL-3.0
from typing import NamedTuple


class Region(NamedTuple):
    """Defines a rectangular region of the screen."""

    x: int
    y: int
    width: int
    height: int
