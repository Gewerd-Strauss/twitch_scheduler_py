from twitchschedulerpy.modules.twitch_scheduler.config import TwitchSchedulerConfigHandler
import datetime
import os
import shutil
import subprocess
from pathlib import Path
from twitchschedulerpy.modules.extensions import ResourceLogger
def check_repository(CH: TwitchSchedulerConfigHandler, RL: ResourceLogger) -> None:
    """
    check if target repository exists.

    :param CH: instance of TwitchSchedulerConfigHandler
    :type CH: TwitchSchedulerConfigHandler
    :param RL: instance of ResourceLogger
    :type RL: ResourceLogger
    """
    Path.exists(CH.synch_repo)


def setup_repository(CH: TwitchSchedulerConfigHandler, RL: ResourceLogger) -> None:
    if not os.path.exists(CH.synch_repo):
        raise FileNotFoundError(f"Directory '{CH.synch_repo}' does not exist")
    git_subdir = Path(CH.synch_repo)  / ".git"
    name = CH.config.GITHUB.name
    email = CH.config.GITHUB.email
    if CH.config.GITHUB.login_via_ssh:
        repo_remote = CH.config.GITHUB.repo_remote_ssh
    else:
        repo_remote = CH.config.GITHUB.repo_remote_https
    if not os.path.exists(git_subdir):
        shutil.rmtree(CH.synch_repo)
        RL.log("setup_repository","clears",CH.synch_repo)
        cmd = (
            f'git clone {repo_remote} "{CH.synch_repo}" && '
            f'git config --local core.autocrlf false && '
            f'git config --local user.email "{email}" && '
            f'git config --local user.name "{name}"'
        )
        subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout= subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        RL.log("setup_repository",f"cloned {repo_remote} into",CH.synch_repo)

    # (reset/fetch/pull)
    cmd = "git reset --hard & git fetch & git pull"

    subprocess.run(
        cmd,
        shell=True,
        cwd=CH.synch_repo,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    RL.log("setup_repository", f"reset, fetched, and pulled into {CH.synch_repo}", repo_remote)


def update_repository(CH: TwitchSchedulerConfigHandler, RL: ResourceLogger):
    timestamp = datetime.datetime.now().isoformat().split(".")[0]
    name = CH.config.GITHUB.name
    email = CH.config.GITHUB.email
    if CH.config.GITHUB.login_via_ssh:
        repo_remote = CH.config.GITHUB.repo_remote_ssh
    else:
        repo_remote = CH.config.GITHUB.repo_remote_https
    for each in (
        ["git", "add", "."],
        ["git", "commit", f"-m'Update {timestamp}'"],
        ["git", "push", "-f"],
    ):
        cwd = CH.synch_repo
        env = os.environ.copy()
        proc = subprocess.Popen(
            args=each,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            text=True,  # or universal_newlines=True (older)
        )
        stdout, stderr = proc.communicate()
        print(f"[EXEC] Spawned: {each}\n\nSTDOUT: {stdout}\n\nSTDERR: {stderr}")

    RL.log("update_repository","pushed to",repo_remote)
