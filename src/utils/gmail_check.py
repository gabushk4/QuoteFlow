"""Vérifie l'accès Gmail en lecture seule et repère les demandes de prix."""

from datetime import datetime, timedelta, timezone
from email.utils import parseaddr
import os
import json
import re
import base64

from src.utils.csv_reader import read_catalogue 

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.constants.file import PROJECT_ROOT



SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
KEYWORD_QUERY ="""{ devis prix soumission "demande de prix" facture demande "demande de soumission" "demande de devis" }"""
DATA_DIR = PROJECT_ROOT / "data"
TOKEN_PATH = DATA_DIR / "gmail_oauth_token.json"
PROCESSED_IDS_FILE = DATA_DIR / "processed_ids.txt"


STOP_WORDS = {"de", "la", "le", "les", "des", "un", "une", "et", "ou", "à", "au", "aux", "du", "dans", "sur", "pour", "par", "avec", "sans"}

def split_keyword(keyword: str) -> list[str]:
    """Splits a keyword into individual words."""
    words = re.findall(r"[^\W\d_]+", keyword.casefold())

    return [
        word for word in words 
        if len(word) > 2 and word not in STOP_WORDS 
    ]

def plurialize(word: str) -> str:
    """Returns the plural form of a word."""
    if word.endswith("s"):
        return word
    elif word.endswith("u"):
        return word + "x"
    elif word.endswith("al"):
        return word[:-2] + "aux"
    else:
        return word + "s"

def sort_by_keywords(message, keywords) -> tuple[int, list[str]]:
    """Returns the score of a message."""      
    score = 0
    found = []

    for keyword in keywords:  
        words = split_keyword(keyword)        
        for word in words:
            forms = {word, plurialize(word)}
            for form in forms:
                pattern = rf"(?<!\w){re.escape(form)}(?!\w)"
                occurences = len(re.findall(pattern, message, flags=re.IGNORECASE))
                if occurences > 0:
                    score += occurences
                    found.append(form)
                    
    return score, found

def find_text_body(part):
    if part.get("mimeType") == "text/plain":
        data = part.get("body", {}).get("data")
        if data:
            data += "=" * (-len(data) % 4)
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    for child in part.get("parts", []):
        text = find_text_body(child)
        if text:
            return text

    return ""
    
def get_credentials():
    "Gets the credentials from the client_secret.json file obtained from Google Cloud Console or from a previously saved token file."
    creds = None
    # If the token was saved previously, load it
    if(TOKEN_PATH.exists()):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        # refresh the token if it's expired and has a refresh token
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, "w") as token_file:
                token_file.write(creds.to_json())

    if not creds or not creds.valid:
        # If there are no (valid) credentials available, let the user log in.    
        creds_data = None
        with open(DATA_DIR / "client_secret.json", "r") as f:
            creds_data = json.load(f)
        creds = InstalledAppFlow.from_client_config(creds_data, SCOPES).run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())
    
    return creds

def make_gmail_client():
    """Returns a Gmail API client."""
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)
    return service.users().messages()

def filter_messages(messages):
    """Filters messages based on which ids are already processed and which are new."""
    processed_ids = set()
    if (PROCESSED_IDS_FILE).exists():
        with open(PROCESSED_IDS_FILE, "r") as f:
            processed_ids = set(f.read().splitlines())
        
    new_messages = [msg for msg in messages if msg["id"] not in processed_ids]    
    return new_messages

def save_processed_ids(messages):
    """Saves the processed message ids to a file."""
    with open(PROCESSED_IDS_FILE, "a") as f:
        for msg in messages:
            f.write(msg["id"] + "\n")

def get_recent_messages(service, days=1):
    """Returns a list of recent messages matching the keyword query."""
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)
    since_timestamp = int(since.timestamp())
    query = f"{KEYWORD_QUERY} after:{since_timestamp}"
    
    response = service.list(userId="me", q=query, maxResults=10).execute()

    messages = filter_messages(response.get("messages", []))

    return messages

def get_message_details(service, message_id):
    """Returns the details of a specific message."""
    return service.get(
        userId="me", 
        id=message_id, 
        format="full",
    ).execute()

def get_email_address(message_details):
    """Returns the email address of the sender."""
    headers = message_details.get("payload", {}).get("headers", [])
    for header in headers:
        if header["name"].lower() == "from":
            from_header = header["value"]
            return parseaddr(from_header)[1]  # Returns the email address part
    raise ValueError("No 'From' header found in message details.")