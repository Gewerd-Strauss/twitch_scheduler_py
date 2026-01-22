from twitchschedulerpy import __version__
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
