from ..core.BaseConfigHandler import BaseConfigHandler
from ..core.config_schema import ConfigSchema


class TwitchSchedulerConfigHandler(BaseConfigHandler):
    def build_schema(self) -> ConfigSchema:
        return TwitchSchedulerSchema()
    def validate(self):
        return super().validate()
    def add_channel(self, channel):
        if channel not in self.applied_settings["CHANNELS"]:
            self.applied_settings["CHANNELS"].append(channel)
            self.save()
            return True
        else:
            return False
    def rem_channel(self, channel):
        if channel not in self.applied_settings["CHANNELS"]:
            return False
        else:
            self.applied_settings["CHANNELS"].remove((channel))
            self.save()
            return True


class TwitchSchedulerSchema(ConfigSchema):

    def defaults(self) -> dict:
        return {
            "GENERAL": {
                
                "open-gist-on-update": False,
                "open-repo-on-update": False,
                "push-to-gist": False,
                "push-to-repo": False,
                "use-repo": False,
                "copy-url": False,
            },
            "CHANNELS": [],
        }

    def validate(self, config: dict) -> None:
        if not isinstance(config["CHANNELS"],list):
            raise TypeError(f"config-section 'CHANNELS' is not of type <list>")
