# #file k ander kya kya ha sab summery
# import os
# import json

# # Extracted Slack export ka folder path
# extract_folder = r"real data"

# message_count = 0
# file_count = 0
# image_count = 0

# # Sirf .json files parse karte hain
# for root, dirs, files in os.walk(extract_folder):
#     for file in files:
#         if file.endswith(".json") and file not in ["channels.json", "users.json"]:
#             file_path = os.path.join(root, file)
#             with open(file_path, "r", encoding="utf-8") as f:
#                 try:
#                     data = json.load(f)
#                     for msg in data:
#                         message_count += 1
#                         if "files" in msg:
#                             for fobj in msg["files"]:
#                                 file_count += 1
#                                 if fobj.get("mimetype", "").startswith("image/"):
#                                     image_count += 1
#                 except Exception as e:
#                     print(f"⚠️ Error reading {file_path}: {e}")

# print("📦 Slack Export Summary")
# print("-" * 40)
# print(f"💬 Total Messages: {message_count}")
# print(f"📂 Attached Files: {file_count}")
# print(f"🖼️ Images: {image_count}")






# # ya data fetch karny k liye 
# import os
# import json
# import requests
# from pathlib import Path

# # ----------------------------
# # CONFIGURATION
# # ----------------------------
# BOT_TOKEN = "YOUR_SLACK_TOKEN"   # apna bot token yahan daalo
# USER_TOKEN = "YOUR_SLACK_TOKEN"  # apna user token yahan daalo

# EXPORT_DIR = Path("slack_export")
# EXPORT_DIR.mkdir(exist_ok=True)

# # ----------------------------
# # Helper Functions
# # ----------------------------
# def slack_api_call(token, endpoint, params=None):
#     url = f"https://slack.com/api/{endpoint}"
#     headers = {"Authorization": f"Bearer {token}"}
#     r = requests.get(url, headers=headers, params=params)
#     data = r.json()
#     if not data.get("ok"):
#         print(f"❌ Error in {endpoint}: {data}")
#     return data


# def save_json(name, data):
#     with open(EXPORT_DIR / f"{name}.json", "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2)


# def fetch_paginated(token, endpoint, key, params=None):
#     results = []
#     cursor = None
#     while True:
#         if cursor:
#             if not params:
#                 params = {}
#             params["cursor"] = cursor
#         resp = slack_api_call(token, endpoint, params)
#         if key in resp:
#             results.extend(resp[key])
#         cursor = resp.get("response_metadata", {}).get("next_cursor")
#         if not cursor:
#             break
#     return results

# # ----------------------------
# # EXPORT FUNCTIONS
# # ----------------------------

# def export_users():
#     print("👥 Fetching users...")
#     users = fetch_paginated(USER_TOKEN, "users.list", "members")
#     save_json("users", users)
#     print(f"✅ {len(users)} users saved.")


# def export_channels(token, name):
#     print(f"📢 Fetching {name} channels...")
#     channels = fetch_paginated(token, "conversations.list", "channels", 
#                                params={"types": "public_channel,private_channel"})
#     save_json(f"{name}_channels", channels)
#     print(f"✅ {len(channels)} {name} channels saved.")
#     return channels


# def export_messages(token, channels, prefix):
#     for ch in channels:
#         cid = ch["id"]
#         cname = ch.get("name", "dm")
#         print(f"💬 Fetching messages for {prefix}:{cname} ({cid})")
#         msgs = fetch_paginated(token, "conversations.history", "messages", {"channel": cid})
#         save_json(f"{prefix}_{cname}_messages", msgs)


# def export_dms():
#     print("📥 Fetching DMs and MPIMs...")
#     dms = fetch_paginated(USER_TOKEN, "conversations.list", "channels", 
#                           params={"types": "im,mpim"})
#     save_json("dms", dms)
#     export_messages(USER_TOKEN, dms, "dm")


# def export_files():
#     print("📂 Fetching files metadata...")
#     files = fetch_paginated(USER_TOKEN, "files.list", "files")
#     save_json("files_metadata", files)
#     print(f"✅ {len(files)} files metadata saved.")


# # ----------------------------
# # MAIN
# # ----------------------------
# if __name__ == "__main__":
#     # 1. Users
#     export_users()

#     # 2. Public & Private Channels (BOT + USER)
#     bot_channels = export_channels(BOT_TOKEN, "bot")
#     user_channels = export_channels(USER_TOKEN, "user")

#     # 3. Messages from channels
#     export_messages(BOT_TOKEN, bot_channels, "bot_channel")
#     export_messages(USER_TOKEN, user_channels, "user_channel")

#     # 4. DMs + Group DMs
#     export_dms()

#     # 5. Files Metadata
#     export_files()

#     print("🎉 Export Completed! Check the 'slack_export' folder.")



import xmlrpc.client
import base64

# =======================
# Odoo credentials
# =======================
url = "http://localhost:8069"       # Odoo server URL
db = "odoo19db"                 # Database name
username = "admin"                  # Odoo username
password = "admin123"                  # Odoo password

# =======================
# Connect to Odoo
# =======================
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

if not uid:
    raise Exception("Authentication failed!")

print(f"✅ Connected to Odoo as UID: {uid}")

# =======================
# Test image upload
# =======================
image_path = "sample.png"  # Replace with your image file path
with open(image_path, "rb") as f:
    image_data = f.read()

encoded_image = base64.b64encode(image_data).decode('utf-8')

# Create attachment
attachment_id = models.execute_kw(db, uid, password,
    'ir.attachment', 'create',
    [{
        'name': 'Test Image',
        'type': 'binary',
        'datas': encoded_image,
        'mimetype': 'image/png',
    }]
)
print(f"✅ Attachment created with ID: {attachment_id}")

# Fetch attachment info (Odoo 19 compatible fields only)
attachment_info = models.execute_kw(db, uid, password,
    'ir.attachment', 'read',
    [attachment_id], {'fields': ['name', 'datas', 'file_size']}
)
print("📄 Attachment info:", attachment_info)

# Web URL to test in browser
print(f"🌐 Access image in browser: {url}/web/content/{attachment_id}?download=true")
