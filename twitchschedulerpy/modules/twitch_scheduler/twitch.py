from requests import Session
from datetime import datetime, timezone
from twitchschedulerpy.modules.twitch_scheduler.config import TwitchSchedulerConfigHandler
def twitch_validate(http: Session, headers: list, CH: TwitchSchedulerConfigHandler) -> None:
    """
    validate api access to twitch's api for pulling channel data
    
    :param http: http socket 
    :param headers: request headers
    :param CH: instance of TwitchSchedulerConfigHandler
    """
    validate_url = "https://id.twitch.tv/oauth2/validate"

    response = http.get(validate_url, headers=headers)

    if response.status_code != 401:
        return  # token is valid

    # Token invalid → refresh
    token_url = "https://id.twitch.tv/oauth2/token"
    payload = {
        "client_id": CH.secrets.get("twitch_client_id"),
        "client_secret": CH.secrets.get("twitch_client_secret"),
        "grant_type": "client_credentials",
    }

    token_response = http.post(token_url, data=payload)
    token_response.raise_for_status()

    token_data = token_response.json()
    access_token = token_data["access_token"]

    # Persist token securely
    CH.secrets.set("twitch_access_token", access_token)

    # Update headers for *this* execution
    headers["Authorization"] = f"Bearer {access_token}"


def twitch_get_http_client() -> Session:
    """
    Set up base Session client to facilitate requests over.
    
    :return: initialised session
    :rtype: Session()
    """
    session = Session()
    session.headers.update({
        "Accept":"application/json",
    })
    return session

def twitch_get_headers(CH) -> list: 
    """
    Load stored required secrets
    - twitch_access_token
    - twitch_client_id

    and returns twitch API header struct

    :param CH: instance of TwitchSchedulerConfigHandler
    :return: header struct
    :rtype: list
    """
    access_token = CH.secrets.get("twitch_access_token")
    client_id = CH.secrets.get("twitch_client_id")

    if not access_token or not client_id:
        raise RuntimeError("Twitch credentials missing in SecretStore")

    return {
        "Authorization": f"Bearer {access_token}",
        "Client-Id": client_id,
    }


###


def twitch_get_broadcaster_id(http: Session, headers: list, channel: str) -> str:
    endpoint = "https://api.twitch.tv/helix/users"
    params = {
        "login": channel.lower(),
    }

    response = http.get(endpoint, headers=headers, params=params)
    response.raise_for_status()

    data = response.json().get("data", [])

    if not data:
        raise ValueError(
            f"Channel name '{channel}' is invalid. "
            "Use the channel name from the Twitch URL, not the display name."
        )

    # Python is 0-based (AHK used data[1])
    return data[0]["id"]


def twitch_get_schedule_ical(http, headers, broadcaster_id: str, channel: str) -> str:
    """
    Fetches the broadcaster's Twitch schedule and returns the iCal text
    containing only future events.
    """
    endpoint = "https://api.twitch.tv/helix/schedule"

    # current UTC time in RFC3339 format (YYYY-MM-DDTHH:MM:SSZ)
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {
        "broadcaster_id": broadcaster_id,
        "start_time": now_utc,
    }
    response = http.get(endpoint, headers=headers, params=params)
    if response.status_code == 400:
        RuntimeWarning(
            f"Bad Request:"
            f"Failed to fetch schedule for broadcaster_id={broadcaster_id} "
            f"(HTTP {response.status_code},"
            f" TEXT {response.text.message})"
        )
        return False
    elif response.status_code == 401:
        RuntimeWarning(
            f"Unauthorized:"
            f"(HTTP   {response.status_code},"
            f" TEXT   {response.text}),"
            f" REASON {response.reason}),"
        )
        return False
    elif response.status_code == 403:
        RuntimeWarning(
            f"Forbidden:"
            f"(HTTP   {response.status_code},"
            f" TEXT   {response.text}),"
            f" REASON {response.reason}),"
        )
        return False
    elif response.status_code == 404:
        RuntimeWarning(
            f"No schedule:"
            f"(HTTP   {response.status_code},"
            f" TEXT   {response.text}),"
            f" REASON {response.reason}),"
        )
        return False
    data = response.json()
    ical_events = []
    for segment in data.get("data", {}).get("segments", []):
        start = segment["start_time"]
        end = segment["end_time"]
        title = segment["title"]
        try:
            category = segment.get("category", {}).get("name", "")
        except:
            category = ""
        uid = segment["id"]
        twitch_url = f"https://www.twitch.tv/{channel}" if channel else ""
        ical_event = (
            f"BEGIN:VEVENT\n"
            f"UID:{uid}\n"
            f"DTSTART:{to_ical_utc(start)}\n"
            f"DTSTAMP:{now_utc}\n"
            f"DTEND:{to_ical_utc(end)}\n"
            f"SUMMARY:{title}\n"
            f"DESCRIPTION:({twitch_url}) {category}\n"
            f"URL:{twitch_url}\n"
            f"END:VEVENT\n"
        )
        ical_events.append(ical_event)
    return "\n\n".join(ical_events)
def to_ical_utc(ts: str) -> str:
    return ts.replace("-","").replace(":","").replace(".000","")
## Build calendar

import re

VCALENDAR_HEADER = """BEGIN:VCALENDAR
PRODID:-//twitch.tv//StreamSchedule//1.0
VERSION:2.0
CALSCALE:GREGORIAN
REFRESH-INTERVAL;VALUE=DURATION:PT6H
X-PUBLISHED-TTL:PT6H
NAME:Streaming Scheduler
X-WR-CALNAME:Streaming Scheduler
"""

VCALENDAR_FOOTER = "END:VCALENDAR\n"


def twitch_build_ical(schedules: dict[str, str]) -> str:
    """
    Build a merged Twitch iCalendar from multiple channel schedules.

    :param schedules: Dict[channel_name, raw iCal string]
    :return: Full VCALENDAR string
    """

    ics_parts: list[str] = [VCALENDAR_HEADER]

    for channel, schedule in schedules.items():
        if not schedule:
            continue

        # Extract VEVENT blocks
        events = re.findall(
            r"BEGIN:VEVENT.*?END:VEVENT",
            schedule,
            flags=re.DOTALL,
        )

        for event in events:
            ics_parts.append(event)
            ics_parts.append("")  # blank line between events

    ics_parts.append(VCALENDAR_FOOTER)

    # Match AHK TZID cleanup
    ics = "\n".join(ics_parts).replace(";TZID=/", ";TZID=")

    return ics
