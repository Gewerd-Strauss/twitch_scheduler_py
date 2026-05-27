import logging
import os.path
import shutil

from twitchschedulerpy.modules.extensions.ResourceLogger import ResourceLogger
from twitchschedulerpy.modules.twitch_scheduler.config import (
    TwitchSchedulerConfigHandler,
)
from twitchschedulerpy import __appname__, __author__, __version__
from twitchschedulerpy.modules.commandline import commandline_setup
from twitchschedulerpy.modules.command_handlers import (
    handle_version,
    handle_all,
    handle_twitch,
    handle_local_file_interface,
    handle_repo,
    handle_ical,
    handle_channels,
    handle_configs,
)
from twitchschedulerpy.modules.git.repo import check_repository, setup_repository
from twitchschedulerpy.modules.utility import (
    convert_format_args,
)

# VERBS:
# channels
#   - add       - add a  new channel to schedule
#   - remove    - remove a currently-scheduled channel
#   - list      - list all currently Stracked channels
# execute
#   - all       - executes pull_twitch, push_repo, trigger_icalSync
#   - twitch    - only queries twitch schedules and rebuilds ical-file locally
#   - repo      - only pushes local ical repo state to repo remote
#   - ical      - (EXPERIMENTAL): only triggers the google script responsible for rebuilding the google calendar from the source ical file /NOT IMPLEMENTED YET
# config
#   - twitch
#       client_id       - set up the client_id for use in API interaction with Twitch. Provide "" to clear contents.
#       client_secret   - set up the client_secret for use in API interaction with Twitch. Provide "" to clear contents.
#       access_token    - set up the access_token for use in API interaction with Twitch. Provide "" to clear contents.

# external


def main():
    RL = ResourceLogger()
    parser = commandline_setup()
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
    elif args.command == "version":
        handle_version(args)
    else:
        args = convert_format_args(args)

        # -------------------------------
        # LOGGING
        # -------------------------------
        logging.basicConfig(level=args["loglevel"])
        # -------------------------------
        # INITIATE CONFIG HANDLER
        # -------------------------------
        RL.log("main", "inits", "config")
        CH = TwitchSchedulerConfigHandler(
            appauthor=__author__,
            appname=__appname__,
            version=__version__,
            loglevel=args["loglevel"],
        )
        if os.path.exists(CH.log_dir):
            shutil.rmtree(CH.log_dir)
            CH.log_dir.mkdir()
            RL.log("main", "clears", CH.log_dir)
        RL.add_log_location(CH.log_dir)
        if args["command"] == "config":
            # -------------------------------
            # HANDLE VERB: CONFIG
            # -------------------------------
            handle_configs(args, RL, CH)
        else:
            # -------------------------------
            # CHECK CONNECTIVITY
            # -------------------------------

            # -------------------------------
            # LOAD CONFIG / INITIATE SETTINGS
            # -------------------------------
            # LOAD GIT SECRET/pageant-PPHRASE
            # -------------------------------

            # -------------------------------
            # CHECK FOR UTILITY UPDATES (LP)
            # -------------------------------

            # -------------------------------
            # REPO: SET UP REPO IF REPO
            # -------------------------------
            # ELSE SET UP GIST
            # -------------------------------

            if args["command"] == "channel":
                # -------------------------------
                # QUERY/MODIFY TWITCH CONFIG
                # -------------------------------
                handle_channels(args, RL, CH)
            elif args["command"] == "execute":
                # -------------------------------
                # EXECUTE SUBMODULES
                # -------------------------------
                if args["action"] == "all":
                    handle_all(RL = RL, CH = CH)
                elif args["action"] == "twitch":
                    ## ENSURE LOCAL TARGET REPOSITORY EXISTS (AND HAS A REMOTE)
                    if not check_repository(CH=CH, RL = RL):
                        setup_repository(CH=CH,RL = RL)

                    ## GENERATE ICAL STRING
                    calendar_ical = handle_twitch(RL, CH)

                    ## ENSURE LOCAL TARGET REPOSITORY EXISTS (AND HAS A REMOTE)
                    ## WRITE ICAL STRING TO FILE WITHIN LOCAL TARGET REPO
                    handle_local_file_interface(calendar_ical, RL, CH)
                elif args["action"] == "repo":
                    handle_repo(RL, CH)
                elif args["action"] == "ical":
                    raise NotImplementedError(
                        "Handle update of google calendar via google ical update script here. experimental feature, not done yet."
                    )
            else:
                raise NotImplementedError(
                    f"The argument {args.command}is not implemented."
                )

    pass


if __name__ == "__main__":
    main()
