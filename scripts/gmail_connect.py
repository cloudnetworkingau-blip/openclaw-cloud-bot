#!/usr/bin/env python3
"""Gmail OAuth connection script using console (headless) flow."""

import json
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']

CLIENT_SECRETS = os.path.expanduser('~/.openclaw/media/inbound/client_secret_786115393397-rirhd6pmfte7irgktuariundrvhfd16a.---06ed32ef-76fc-49d7-988f-c7ca6a7ce4c3.json')
CREDENTIALS_FILE = os.path.expanduser('~/.openclaw/credentials/gmail_credentials.json')

def main():
    from google_auth_oauthlib.flow import InstalledAppFlow

    # Load client secrets
    with open(CLIENT_SECRETS) as f:
        client_config = json.load(f)

    # Run console flow (headless-friendly)
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    credentials = flow.run_console()

    # Save credentials
    os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump({
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': list(credentials.scopes) if credentials.scopes else SCOPES
        }, f)

    print(f"Credentials saved to {CREDENTIALS_FILE}")

    # Test: fetch Gmail profile
    from googleapiclient.discovery import build
    service = build('gmail', 'v1', credentials=credentials)
    profile = service.users().getProfile(userId='me').execute()
    print(f"✅ Connected to Gmail: {profile.get('emailAddress')}")
    print(f"   Messages total: {profile.get('messagesTotal')}")
    print(f"   Threads total: {profile.get('threadsTotal')}")

if __name__ == '__main__':
    main()
