import argparse
from appdirs import user_config_dir
from pathlib import Path
import os


def commandline_setup():
    parser = argparse.ArgumentParser(
        description="""
        Utility for converting a single note within an 'Obsidian.md'-vault to formats
        supported by the open-source publishing system 'Quarto', and then optionally 
        converting them via 'Quarto'.
        
        TODO: finish the description and triple-check the texts of all help arguments.
        TODO: write description-texts for all parsers, take a look at the output of
        `python -m obsidianknittrpy processingmodules -h` for details about how to
        implement this.
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- 'channel' command setup ---
    channel_parser = subparsers.add_parser(
        "channel",
        help="Manage Twitch Channels",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
        Manage Twitch Channels

        Add/Remove a twitch channel to/from the calendar, or return/list all channels currently tracked.
        """,
    )
    channel_parser_setup(channel_parser)
    # --- 'version' command setup ---
    version_parser = subparsers.add_parser("version", help="Get the version.")
    version_parser = version_parser_setup(version_parser)
    # --- 'execute' command setup ---
    execute_parser = subparsers.add_parser(
        "execute",
        help="Execute Routines",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
        Execute different parts of the utility's toolkit.

        
        """,
    )
    execute_parser_setup(execute_parser)
    # --- 'config' command setup ---
    config_parser = subparsers.add_parser(
        "config",
        help="Modify configuration of utility / provide API credentials.",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
        Set / remove / update the following credentials required to interact with external services:

        TWITCH:
        twitchschedulerpy config [twitch] [client_id: str|client_secret: str|access_token: str]
            - add / modify / remove the 3 pieces of twitch API verification required:
        """,
    )
    config_parser_setup(config_parser)
    return parser


def common_arguments3(parser):
    """Add common arguments to each subcommand."""
    parser.add_argument(
        "pass_through",
        nargs="*",
        # help="""
        # Pass-through arguments in format 'namespace::key=value'`nValid Examples:\n- "
        # + "quarto::pdf.author=Ballos"
        # + "\n- "
        # + "quarto::html.author=Professor E GADD"
        # + "\n- "
        # + "quarto::docx.author=Zote the mighty, a knight of great renown
        # """,
        help="""
        Pass-through arguments in format 'namespace::key=value'
        Valid Examples:
        \t- "quarto::pdf.author=Ballos"
        \t- "quarto::html.author=Professor E GADD"
        \t- "quarto::docx.author=Zote the mighty, a knight of great renown"
        """,
    )

def common_arguments2(parser):
    """Add common arguments to each subcommand."""
    parser.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level (default: INFO)",
    )
def common_arguments(parser):
    """Add common arguments to each subcommand."""
    parser.add_argument(
        "-i",
        "--id",
        required=False,
        help="Channel-ID",
    )
    parser.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level (default: INFO)",
    )
        # Add pass-through argument
    parser.add_argument(
        "pass_through",
        nargs="*",
        # help="""
        # Pass-through arguments in format 'namespace::key=value'`nValid Examples:\n- "
        # + "quarto::pdf.author=Ballos"
        # + "\n- "
        # + "quarto::html.author=Professor E GADD"
        # + "\n- "
        # + "quarto::docx.author=Zote the mighty, a knight of great renown
        # """,
        help="""
Pass-through arguments in format 'namespace::key=value'
Valid Examples:
\t- "quarto::pdf.author=Ballos"
\t- "quarto::html.author=Professor E GADD"
\t- "quarto::docx.author=Zote the mighty, a knight of great renown"
""",
    )
    # Add more common arguments as needed


def config_parser_setup(config_parser):
    config_subparsers = config_parser.add_subparsers(dest="action",required = True)
    twitchconfig_parser = config_subparsers.add_parser(
        "twitch",
        help="Set/unset config data related to Interaction with Twitch/its API",
        description="""
        Provide the following structure:
        twitchschedulerpy config twitch [client-id <str>] [client-secret <str>]|[access-token <str>]
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    twitchconfig_parser.add_argument(
        "--client-id",
        dest="client_id",
        type=str,
        help="Set/Unset Twitch application Client ID",
    )
    twitchconfig_parser.add_argument(
        "--client-secret",
        dest="client_secret",
        type=str,
        help="Set/Unset Twitch application Client Secret",
    )
    twitchconfig_parser.add_argument(
        "--access-token",
        dest="access_token",
        type=str,
        help="Set/Unset Twitch API Access Token"
    )
    common_arguments2(twitchconfig_parser)
    common_arguments3(twitchconfig_parser)
def execute_parser_setup(execute_parser):
    execute_subparsers = execute_parser.add_subparsers(dest="action", required=True)
    # 'all' suboption
    all_parser = execute_subparsers.add_parser(
        "all",
        help="Execute complete Toolkit",
        description="""
        This will trigger:
        1. Collection of up-to-date schedules for all tracked Twitch Channels
        2. Creation of local `schedule.ical`-file
        3. Pushing the local repository's schedule file to remote git repository
        4. Experimental/NOTIMPLEMENTED: Triggering a rebuild of the google Calendar via google ical-update-script (or internal method?)
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    common_arguments2(all_parser)
    # 'twitch' suboption
    twitch_parser = execute_subparsers.add_parser(
        "twitch",
        help="Execute Collection of twitch-Schedules and generate local ical file in repository",
        description="""
        This will trigger:
        1. Collection of up-to-date schedules for all tracked Twitch Channels
        2. Creation of local `schedule.ical`-file in local git repository
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    common_arguments2(twitch_parser)

    # 'repo' suboption
    repo_parser = execute_subparsers.add_parser(
        "repo",
        help="Push local git repository to remote; (force-overwriting remote state)",
        description="""
        This will trigger:
        3. Pushing local git repository to remote
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    common_arguments2(repo_parser)
    repo_parser_setup(repo_parser)

    # 'ical' suboption
    ical_parser = execute_subparsers.add_parser(
        "ical",
        help="Execute the google-script required to force-refresh the Google Calendar",
        description="""
        NOT IMPLEMENTED.
        This will execute the google script required to forcefully refresh the 
        google-calendar's representation of the schedule Calendar. This can be necessary
        because google's calendar is prone to not respect changes of the associated online
        `.ical`-file.
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    common_arguments2(ical_parser)
    ical_parser_setup(ical_parser)

def channel_parser_setup(channel_parser):
    # GUI-specific options
    channel_subparsers = channel_parser.add_subparsers(dest="action", required=True)
    # 'add' command
    add_parser = channel_subparsers.add_parser(
        "add",
        help="Add a Channel ID to the Schedule-Collection Routine",
        description="""
        Add a Twitch Channel to the Channel-Schedule-Collection-routine, to be queried when utility is executed.
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )
    add_parser.add_argument(
        "channel",
        type=str,
        help="Twitch channel name or ID to add",
    )
    common_arguments(add_parser)  # Reuse shared arguments for 'gui'
    # 'remove' command
    remove_parser = channel_subparsers.add_parser(
        "remove",
        help="Remove a Channel ID from the Schedule-Collection Routine",
        description="""
        Remove a Twitch Channel from the Channel-Schedule-Collection-routine, to no longer be queried when utility is executed.
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )
    remove_parser.add_argument(
        "--client-id",
        dest="client_id",
        type=str,
        help="Set/Unset Twitch application Client ID",
    )
    common_arguments(remove_parser)  # Reuse shared arguments for 'gui'
    # 'list' command
    list_parser = channel_subparsers.add_parser(
        "list",
        help="List all Channels (by ID) that are currently managed by the utility.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    common_arguments(list_parser)  # Reuse shared arguments for 'gui'


def ical_parser_setup(ical_parser):
    pass
def repo_parser_setup(repo_parser):
    repo_parser.add_argument(
        '--force',
        "-f",
        default=False,
        action="store_true",
        help="Force push git repo to remote",
    )
    repo_parser.add_argument(
        '--rebase',
        "-r",
        default=False,
        action="store_true",
        help="rebase instead of merge",
    )


def version_parser_setup(version_parser):
    version_parser.add_argument(
        "--clean",
        "-c",
        default=False,
        action="store_true",
        help="Return version number without descriptor-string.",
    )
