from ..core.BaseConfigHandler import BaseConfigHandler
from ..core.config_schema import ConfigSchema
from pathlib import Path

class TwitchSchedulerConfigHandler(BaseConfigHandler):
    def __init__(self, *, appname, appauthor, version, loglevel = None, is_gui = None):
        super().__init__(appname=appname, appauthor=appauthor, version=version, loglevel=loglevel, is_gui=is_gui)
        self.synch_repo = Path(self.application_directory) / "sync_repo"
        self.synch_repo.mkdir(exist_ok=True)
        
    def build_schema(self) -> ConfigSchema:
        return TwitchSchedulerSchema()
    def validate(self):
        return super().validate()
    def add_channel(self, channel):
        channels = self.raw_settings["CHANNELS"]
        if channel in channels:
            return False
        channels.append(channel)
        self.config = self.schema.build(self.raw_settings)
        self.save()
        return True
    def rem_channel(self, channel):
        channels = self.raw_settings["CHANNELS"]
        if channel not in channels:
            return False
        channels.remove(channel)
        self.config = self.schema.build(self.raw_settings)
        self.save()
        return True

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class GeneralConfig:
    open_gist_on_update: bool = False
    open_repo_on_update: bool = False
    push_to_gist: bool = False
    push_to_repo: bool = False
    use_repo: bool = False
    copy_url: bool = False


@dataclass
class GitHubConfig:
    gist: int = -1
    repo: Path = Path()
    name: str = ""
    email: str = ""
    login_via_ssh: bool = False


@dataclass
class MiscConfig:
    open_gist_repo_on_update: bool = False

@dataclass
class TwitchSchedulerConfig:
    GENERAL: GeneralConfig = field(default_factory=GeneralConfig)
    CHANNELS: List[str] = field(default_factory=list)
    GITHUB: GitHubConfig = field(default_factory=GitHubConfig)
    MISCELLANEOUS: MiscConfig = field(default_factory=MiscConfig)


class TwitchSchedulerSchema(ConfigSchema):
    config_model = TwitchSchedulerConfig
