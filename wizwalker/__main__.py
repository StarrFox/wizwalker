from sys import platform

from wizwalker import WizWalker
from wizwalker.cli import WizWalkerCli


def main():
    if platform != "win32":
        raise RuntimeError(f"This program is windows only, not {platform}")

    walker = WizWalker()
    cli = WizWalkerCli(walker)
    cli.run()

    # app = WizWalker()
    #
    # # close WizWalker when app is closed
    # atexit.register(app.close)
    #
    # app.run()


if __name__ == "__main__":
    main()
