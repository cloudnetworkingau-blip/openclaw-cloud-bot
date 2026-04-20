#!/usr/bin/env python3
"""Gmail OAuth - Step 1: Generate authorization URL."""

import json
import os
import urllib.parse

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']

CLIENT_SECRETS = os.path.expanduser('~/.openclaw/media/inbound/client_secret_786115393397-rirhd6pmfte7irgktuariundrvhfd16a.---06ed32ef-76fc-49d7-988f-c7ca6a7ce4c3.json')

with open(CLIENT_SECRETS) as f:
    client_config = json.load(f)

installed = client_config['installed']
client_id = installed['client_id']
auth_uri = installed['auth_uri']
redirect_uris = installed['redirect_uris']
redirect_uri = redirect_uris[0]  # http://localhost

# Generate random state and build auth URL
import secrets
state = secrets.token_urlsafe(16)
auth_url = (f"{auth_uri}?"
            f"client_id={client_id}&"
            f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
            f"response_type=code&"
            f"scope={'+'.join(SCOPES)}&"
            f"access_type=offline&"
            f"prompt=consent&"
            f"state={state}")

print("=" * 60)
print("GMAIL OAUTHORIZATION - STEP 1")
print("=" * 60)
print()
print("Open this URL in your browser:")
print()
print(auth_url)
print()
print(f"State token (save this for Step 2): {state}")
print()
print("After you authorize, you'll be redirected to:")
print(f"  {redirect_uri}?code=XXXXX&state={state}")
print()
print("Copy the 'code' value from that redirect URL and paste it back.")
print()
