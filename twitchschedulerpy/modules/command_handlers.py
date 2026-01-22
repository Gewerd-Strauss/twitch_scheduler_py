from twitchschedulerpy import __version__
from twitchschedulerpy.modules.twitch_scheduler.twitch import (
    twitch_validate,
    twitch_get_http_client,
    twitch_get_headers,
    twitch_get_broadcaster_id,
    twitch_get_schedule_ical,
    twitch_build_ical
)
import logging
def handle_version(args):
    """Handle the 'version' command."""
    if args.clean:
        print(__version__)
    else:
        print(f"Current version: {__version__}")
    exit(0)

def handle_configs(args, RL, CH):
    logging.basicConfig(level=args["loglevel"])
    RL.log("main","inits","config")
    if args["action"]=="twitch":
        if args["client_id"] is not None:
            RL.log("handle_configs", "set", "twitch_client_id")
            CH.secrets.set("twitch_client_id",args["client_id"])
        if args["client_secret"] is not None:
            RL.log("handle_configs", "set", "client_secret")
            CH.secrets.set("twitch_client_secret",args["client_secret"])
            RL.log("handle_configs", "set", "client_secret")
        if args["access_token"] is not None:
            RL.log("handle_configs", "set", "access_token")
            CH.secrets.set("twitch_access_token",args["access_token"])
    else:
        raise NotImplementedError("config handling is not yet set up for components other than twitch.")
    return
def handle_twitch(args, RL, CH) -> str:
    http = twitch_get_http_client()
    headers = twitch_get_headers(CH)
    twitch_validate(http,headers,CH)
    schedules = {}
    for channel in CH.applied_settings["CHANNELS"]:

        # resolve broadcaster id
        broadcaster_id = twitch_get_broadcaster_id(
            http=http, headers=headers, channel=channel
        )
        RL.log("twitch", "resolve", f"broadcaster_id for {channel}: {broadcaster_id}")

        # pull channel schedule
        ical_text = twitch_get_schedule_ical(
            http=http, headers=headers, broadcaster_id=broadcaster_id
        )
        RL.log("twitch", "resolve", f"broadcaster_id for {channel}: {broadcaster_id}")
        print(ical_text[:500])
        schedules[channel] = ical_text
    calendar_ical = twitch_build_ical(schedules=schedules)
    return calendar_ical
    raise NotImplementedError("The callback for verb 'twitch' is not implemented yet.")
def handle_channels(args, RL, CH):
    if args["action"]=="add":
        CH.add_channel(args["channel"])
        RL.log("handle_channels","added channel",args["channel"])
    elif args["action"]=="remove":
        CH.rem_channel(args["channel"])
        RL.log("handle_channels","removed channel",args["channel"])
    elif args["action"]=="list":
        raise NotImplementedError("The callback for verb 'channels' is not implemented yet.")
    return
