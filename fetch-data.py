import os
import json
import time
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ------------------------------
# CONFIG
# ------------------------------
BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "YOUR_SLACK_TOKEN")
USER_TOKEN = os.getenv("SLACK_USER_TOKEN", "YOUR_SLACK_TOKEN")

EXPORT_DIR = "slack_export"
FILES_DIR = os.path.join(EXPORT_DIR, "files")
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

bot_client = WebClient(token=BOT_TOKEN)
user_client = WebClient(token=USER_TOKEN)

# ------------------------------
# Helper Functions
# ------------------------------
def save_json(data, filename):
    with open(os.path.join(EXPORT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def slack_api_call(client, func, **kwargs):
    """Wrapper with error handling and rate limit handling"""
    while True:
        try:
            resp = func(**kwargs)
            return resp
        except SlackApiError as e:
            if e.response["error"] == "ratelimited":
                retry_after = int(e.response.headers.get("Retry-After", 30))
                print(f"⏳ Rate limited. Sleeping {retry_after}s...")
                time.sleep(retry_after)
                continue
            else:
                print(f"❌ Error in {func.__name__}: {e.response.data}")
                return None

def fetch_paginated(client, func, key, **kwargs):
    """Generic pagination fetcher"""
    items = []
    cursor = None
    while True:
        if cursor:
            kwargs["cursor"] = cursor
        resp = slack_api_call(client, func, **kwargs)
        if not resp:
            break
        items.extend(resp[key])
        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
    return items

# ------------------------------
# File Downloader
# ------------------------------
def download_file(file_obj, token):
    url = file_obj.get("url_private")
    if not url:
        return None
    filename = f"{file_obj['id']}_{file_obj['name']}"
    filepath = os.path.join(FILES_DIR, filename)

    if os.path.exists(filepath):
        return filepath  # skip already downloaded

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, stream=True)

    if resp.status_code == 200:
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"📂 Downloaded: {filename}")
        return filepath
    else:
        print(f"❌ Failed to download {filename} ({resp.status_code})")
        return None

# ------------------------------
# Export Functions
# ------------------------------
def export_users():
    print("👥 Fetching users...")
    users = fetch_paginated(user_client, user_client.users_list, "members")
    save_json(users, "users.json")
    print(f"✅ {len(users)} users saved.")

def export_channels():
    print("📢 Fetching bot channels...")
    bot_channels = fetch_paginated(bot_client, bot_client.conversations_list, "channels", types="public_channel,private_channel")
    save_json(bot_channels, "bot_channels.json")
    print(f"✅ {len(bot_channels)} bot channels saved.")

    print("📢 Fetching user channels...")
    user_channels = fetch_paginated(user_client, user_client.conversations_list, "channels", types="public_channel,private_channel")
    save_json(user_channels, "user_channels.json")
    print(f"✅ {len(user_channels)} user channels saved.")

    return bot_channels, user_channels

def export_messages(channels, label, client, token):
    for ch in channels:
        cid = ch["id"]
        name = ch.get("name", "dm")
        print(f"💬 Fetching messages for {label}:{name} ({cid})")

        messages = fetch_paginated(client, client.conversations_history, "messages", channel=cid, limit=1000)

        # Download files if exist
        for msg in messages:
            if "files" in msg:
                for f in msg["files"]:
                    download_file(f, token)

        save_json(messages, f"{label}_{cid}.json")

def export_dms():
    print("📥 Fetching DMs and MPIMs...")
    ims = fetch_paginated(user_client, user_client.conversations_list, "channels", types="im,mpim")
    for dm in ims:
        cid = dm["id"]
        print(f"💬 Fetching messages for dm:{cid}")
        messages = fetch_paginated(user_client, user_client.conversations_history, "messages", channel=cid, limit=1000)

        # Download attached files
        for msg in messages:
            if "files" in msg:
                for f in msg["files"]:
                    download_file(f, USER_TOKEN)

        save_json(messages, f"dm_{cid}.json")

def export_files_metadata():
    print("📂 Fetching files metadata...")
    files = fetch_paginated(user_client, user_client.files_list, "files", count=200)
    save_json(files, "files.json")
    print(f"✅ {len(files)} files metadata saved.")

# ------------------------------
# MAIN
# ------------------------------
if __name__ == "__main__":
    export_users()
    bot_channels, user_channels = export_channels()

    export_messages(bot_channels, "bot_channel", bot_client, BOT_TOKEN)
    export_messages(user_channels, "user_channel", user_client, USER_TOKEN)

    export_dms()
    export_files_metadata()

    print("🎉 Export Completed! Check the 'slack_export' folder.")
