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
    elif args["action"] == "github":
        if "email" in args:
            if args["email"] is not None:
                CH.config.GITHUB.email = args["email"]
                RL.log(
                    "handle_configs", "set", f"git commit email to {args["email"]}"
                )
                
        if "gist" in args:
            if args["gist"] is not None and isinstance(args["gist"],str):
                CH.config.GITHUB.gist = args["gist"]
                RL.log(
                    "handle_configs", "set", f"gist flag to {args["gist"]}"
                )

        if "login_via_ssh" in args:
            if args["login_via_ssh"] is not None and isinstance(args["login_via_ssh"],bool):
                CH.config.GITHUB.login_via_ssh = args["login_via_ssh"]
                RL.log(
                    "handle_configs", "set", f"git-remote type to {"ssh" if args["login_via_ssh"] else "https"}"
                )
        if "name" in args:
            if args["name"] is not None:
                CH.config.GITHUB.name = args["name"]
                RL.log(
                    "handle_configs", "set", f"github-username to {args["name"]}"
                )
        if "repo" in args:
            if args["repo"] is not None:
                CH.config.GITHUB.repo = args["repo"]
                RL.log(
                    "handle_configs", "set", f"git-repo to {args["repo"]}"
                )
        if "repo_remote" in args:
            if args["repo_remote"] is not None:
                CH.config.GITHUB.repo_remote = args["repo_remote"]
                RL.log(
                    "handle_configs", "set", f"repository remote to {args["repo_remote"]}"
                )
        CH.save()
        pass

    else:
        raise NotImplementedError("config handling is not yet set up for components other than twitch.")
    return


def handle_all():
    raise NotImplementedError("The callback for verb 'all' is not implemented yet.")

def handle_local_file_interface(calendar_ical, args, RL, CH):
    raise NotImplementedError("The writing of the file to a file location is not implemented because first we must set up: "
                              + "\n- the config toggles for what type (repo vs gist),"
                              + "\n- where that repo is placed,"
                              + "\n- the repo-setup utility itself"
                              + "\n- and probably more stuff"
                              )
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
def handle_repo():
    raise NotImplementedError("The callback for verb 'repo' is not implemented yet.")
def handle_ical():
    raise NotImplementedError("The callback for verb 'ical' is not implemented yet.")


def handle_channels(args, RL, CH):
    if args["action"]=="add":
        for channel in args["channels"]:
            CH.add_channel(channel)
            RL.log("handle_channels", "added channel", channel)
    elif args["action"]=="remove":
        for channel in args["channels"]:
            CH.rem_channel(channel)
            RL.log("handle_channels","removed channel",channel)
    elif args["action"]=="list":
        raise NotImplementedError("The callback for verb 'channels' is not implemented yet.")
    return
