import os
import datetime
import pytz
import re as regex

from dotenv import load_dotenv


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
scopes = ["https://www.googleapis.com/auth/calendar"]

CREDENTIALS = os.getenv("GOOGLE_OAUTH_CREDENTIALS")

SENDER_EMAIL = os.getenv("SENDER_EMAIL")

TOKEN_PATH = os.getenv("TOKEN_JSON")

creds = None

# "token.json" stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first time
# stored in environment variable for privacy

if os.path.exists(TOKEN_PATH):
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, scopes)

# if there are no valid credentials available, let user log in
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, scopes)
        creds = flow.run_local_server(port=0)

    # save credentials for the next run
    with open(TOKEN_PATH, "w") as token:
        token.write(creds.to_json())


# gmail api
gmail_service = build("gmail", "v1", credentials=creds)

# calendar api
calendar_service = build("calendar", "v3", credentials=creds)


# service = build("gmail", "v1", credentials=creds)

# search for messages from specific sender
query = f"from:{SENDER_EMAIL}"
response = gmail_service.users().messages().list(userId="me", q=query).execute()

# print the subjects of all matching messages
if "messages" in response:
    # print(f'Found {len(response["messages"])} messages:')
    for message in response["messages"]:
        msg = (
            gmail_service.users()
            .messages()
            .get(userId="me", id=message["id"])
            .execute()
        )

        headers = msg["payload"]["headers"]

        for header in headers:
            if header["name"] == "Subject":
                openMailSubject = header["value"]

                # if subject matches this format, add it to the calendar
                match = regex.search(
                    r"Hooray! You have a new class at ([a-zA-Z]{3}, [a-zA-Z]{3} \d{1,2}, \d{4} \d{1,2}:\d{2} [AP]M [a-zA-Z ]+)$",
                    openMailSubject,
                )

                if match:
                    start_time_str = match.group(1)
                    start_time_utc = datetime.datetime.strptime(
                        start_time_str, "%a, %b %d, %Y %I:%M %p %Z"
                    ).replace(tzinfo=pytz.timezone("US/Eastern"))

                    eastern_tz = pytz.timezone("US/Eastern")
                    start_time_eastern = eastern_tz.normalize(
                        eastern_tz.localize(start_time_utc)
                    )
                    end_time_eastern = start_time_eastern + datetime.timedelta(hours=1)
                    event = {
                        "summary": "New Class",
                        "location": "Online",
                        "description": "A new class has been scheduled.",
                        "start": {
                            "dateTime": start_time_eastern.strftime(
                                "%Y-%m-%dT%H:%M:%S"
                            ),
                            "timeZone": "US/Eastern",
                        },
                        "end": {
                            "dateTime": end_time_eastern.strftime("%Y-%m-%dT%H:%M:%S"),
                            "timeZone": "US/Eastern",
                        },
                        "reminders": {
                            "useDefault": True,
                        },
                    }
                    event = (
                        calendar_service.events()
                        .insert(calendarId="primary", body=event)
                        .execute()
                    )
                    print(f'Event created: {event.get("htmlLink")}')
                    # print(f"Subject: {openMailSubject}")

else:
    print("No messages found.")


# except HttpError as error:
#     # TODO(developer) - Handle errors from gmail API.
#     print(f"An error occurred: {error}")
