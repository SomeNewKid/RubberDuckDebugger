"""Bootstrap the command-line application."""

import asyncio

from . import cli


def main() -> None:
    """Run the command-line application."""
    asyncio.run(cli.main())


if __name__ == "__main__":
    main()
