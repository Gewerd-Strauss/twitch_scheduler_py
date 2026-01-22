from twitchschedulerpy import __version__
import logging
def handle_version(args):
    """Handle the 'version' command."""
    if args.clean:
        print(__version__)
    else:
        print(f"Current version: {__version__}")
    exit(0)

