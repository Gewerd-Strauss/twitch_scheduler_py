from ..core.BaseConfigHandler import BaseConfigHandler
from ..core.config_schema import ConfigSchema


class TwitchSchedulerConfigHandler(BaseConfigHandler):
    def build_schema(self) -> ConfigSchema:
        return TwitchSchedulerSchema()
    def validate(self):
        return super().validate()
    


class TwitchSchedulerSchema(ConfigSchema):

    def defaults(self) -> dict:
        return {
            "GENERAL": {...},
            "CHANNELS": {...},
        }

    def validate(self, config: dict) -> None:
        if not config["CHANNELS"]:
            raise ValueError("No channels configured")
        
