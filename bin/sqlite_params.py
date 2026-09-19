#!/usr/bin/env python3
"""Execute one SQLite statement with command-line values bound as parameters."""

import sqlite3
import sys


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: sqlite_params.py <database> <sql> [value ...]")

    database, sql, *values = sys.argv[1:]
    with sqlite3.connect(database) as connection:
        cursor = connection.execute(sql, values)
        for row in cursor:
            print("|".join("" if value is None else str(value) for value in row))


if __name__ == "__main__":
    main()
