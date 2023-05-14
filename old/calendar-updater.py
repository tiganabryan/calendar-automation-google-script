import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# sentitive info like emails and keys needs to be saved in a .env file and referenced using os.environ
# allow the account your google cloud project was made with access to your email, if they aren't the same. you can do this in gmail settings

# load_dotenv(dotenv_path=env_path)

load_dotenv()
# create environment variable for my service account key. then reference it here so the key is never public
path_to_oauth = os.getenv("GOOGLE_OAUTH_CREDENTIALS")
# API_KEY = os.getenv("API_KEY")

# service = build("gmail", "v1", developerKey=API_KEY)


# Replace with your email address
MY_EMAIL = os.getenv("MY_EMAIL")
print(os.getenv("MY_EMAIL"))

# Replace with the email address of the sender you want to search for
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

# get credentials from the service account json environment variable
# Authenticate and construct the service object


credentials = Credentials.from_authorized_user_file(
    path_to_oauth, scopes=["https://www.googleapis.com/auth/gmail.readonly"]
)

service = build("gmail", "v1", credentials=credentials.installed)

# Search for messages from the specified sender
query = f"from:{SENDER_EMAIL}"
# print(service.users())

response = service.users().messages().list(userId=MY_EMAIL, q=query).execute()

# Print the message IDs of matching messages
if "messages" in response:
    print(f'Found {len(response["messages"])} messages:')
    for message in response["messages"]:
        print(f' - {message["id"]}')
else:
    print("No messages found.")
