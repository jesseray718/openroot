# SPDX-License-Identifier: GPL-3.0
"""The `generics` module is a backport module from V1."""

from ._migration import getattr_migration

__getattr__ = getattr_migration(__name__)
