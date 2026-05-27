from ..core.BaseConfigHandler import BaseConfigHandler
from ..core.config_schema import ConfigSchema
from pathlib import Path

class TwitchSchedulerConfigHandler(BaseConfigHandler):
    def __init__(self, *, appname, appauthor, version, loglevel = None, is_gui = None):
        super().__init__(appname=appname, appauthor=appauthor, version=version, loglevel=loglevel, is_gui=is_gui)
        self.synch_repo = Path(self.application_directory) / "sync_repo"
        self.synch_repo.mkdir(exist_ok=True)
        self.initialize()

    def build_schema(self) -> ConfigSchema:
        return TwitchSchedulerSchema()
    def validate(self):
        if self.config.GENERAL.use_repo and not self.config.GITHUB.repo:
            raise ValueError("use_repo=True requires GITHUB.repo to be set to TRUE")
        if self.config.GENERAL.push_to_gist and self.config.GITHUB.gist < 0:
            raise ValueError("push_to_gist=True requires a valid gist id")
        if self.config.GENERAL.push_to_repo and self.config.GENERAL.push_to_gist:
            raise ValueError("push_to_repo and push_to_gist are mutually exclusive")
        if self.config.GENERAL.use_repo and not self.synch_repo.exists():
            raise RuntimeError("sync repo directory missing")
        # normalize declared channels.
        self.config.CHANNELS = sorted(set(self.config.CHANNELS))

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
    def list_channels(self):
        for i in self.get_section("CHANNELS"):
            print(i)
    def post_init(self):
        print("CUSTOM POST INIT PIPELINE")
        return super().post_init()
    def post_load(self):
        print("CUSTOM POST LOAD PIPELINE")
        return super().post_load()

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
    repo: Path = ""
    repo_remote_ssh: str = ""
    repo_remote_https: str = ""
    name: str = ""
    email: str = ""
    repo_remote: str = ""
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
