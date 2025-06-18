#!/usr/bin/env python3

from os import environ
from pathlib import Path
from sys import exit, stderr, path as py_path

ROOT = Path(__file__).parent
environ.setdefault(
    "BERNARD_SETTINGS_FILE",
    str(ROOT / "src/with_rocket_bot/settings.py"),
)

if __name__ == "__main__":
    try:
        py_path.append(str(ROOT / "src"))
        from bernard.misc.main import main
        from bernard.conf import settings

        if settings.DEV:
            from dev_bootstrap import setup

            setup()

        main()
    except ImportError as e:
        print(e)
        print(  # noqa: T201 - No ``print`` statements in production code.
            "Could not import BERNARD. Is your environment correctly " "configured?",
            file=stderr,
        )
        exit(1)
