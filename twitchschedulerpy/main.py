import logging
from twitchschedulerpy.modules.extensions.ResourceLogger import ResourceLogger
from twitchschedulerpy.modules.commandline import commandline_setup
from twitchschedulerpy.modules.command_handlers import (
    handle_version,
)
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


    pass

if __name__ == "__main__":
    main()
