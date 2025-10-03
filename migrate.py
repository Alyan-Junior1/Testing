# import requests
# import xmlrpc.client

# # Slack setup
# slack_token = "YOUR_SLACK_TOKEN"
# headers = {"Authorization": f"Bearer {slack_token}"}

# # Odoo setup
# url = "http://localhost:8069"
# db = "odoo19db"
# username = "admin"
# password = "admin123"

# common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
# uid = common.authenticate(db, username, password, {})
# models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# # 1. Get channels from Slack
# resp = requests.get("https://slack.com/api/conversations.list", headers=headers)
# channels = resp.json().get("channels", [])

# for ch in channels:
#     channel_name = ch["name"]
#     # Odoo Discuss channel create
#     channel_id = models.execute_kw(
#         db, uid, password,
#         "discuss.channel", "create",
#         [{"name": channel_name, "channel_type": "channel"}]
#     )
    
#     # 2. Get messages for this channel
#     history = requests.get(
#         "https://slack.com/api/conversations.history",
#         headers=headers,
#         params={"channel": ch["id"]}
#     ).json()
    
#     for msg in history.get("messages", []):
#         text = msg.get("text", "")
#         if text:
#             models.execute_kw(
#                 db, uid, password,
#                 "mail.message", "create",
#                 [{
#                     "model": "discuss.channel",
#                     "res_id": channel_id,
#                     "body": text,
#                 }]
#             )

import os
import base64
import json
import xmlrpc.client

# ========== ODOO CONNECTION ==========
ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo19db"
ODOO_USER = "admin"
ODOO_PASS = "admin123"

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
if not uid:
    raise Exception("❌ Odoo login failed!")

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
print(f"✅ Connected to Odoo 19 as UID: {uid}")

# ========== SLACK EXPORT FOLDER ==========
EXPORT_DIR = "slack_export"
FILES_DIR = os.path.join(EXPORT_DIR, "files")

# Load channels (bot + user)
channels_data = []
for fname in ["bot_channels.json", "user_channels.json"]:
    path = os.path.join(EXPORT_DIR, fname)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            channels_data.extend(json.load(f))

# Load users
users_map = {}
users_path = os.path.join(EXPORT_DIR, "users.json")
if os.path.exists(users_path):
    with open(users_path, "r", encoding="utf-8") as f:
        for u in json.load(f):
            users_map[u["id"]] = u.get("real_name", u.get("name", "Unknown"))

# ========== CREATE DISCUSS CHANNELS ==========
channel_map = {}
for ch in channels_data:
    ch_name = ch.get("name") or "unnamed"
    channel_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASS,
        "discuss.channel", "create",
        [{"name": f"Slack - {ch_name}"}]
    )
    channel_map[ch["id"]] = {"odoo_id": channel_id, "name": ch_name}
    print(f"💬 Created Discuss Channel: {ch_name} → {channel_id}")

# ========== FUNCTION TO MIGRATE MESSAGES ==========
def migrate_messages(channel_id, channel_name):
    odoo_channel_id = channel_map[channel_id]["odoo_id"]

    # Case 1: messages_<channel_id>.json
    file_path = os.path.join(EXPORT_DIR, f"messages_{channel_id}.json")
    messages = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            messages = json.load(f)

    # Case 2: folder structure slack_export/<channel_name>/*.json
    folder_path = os.path.join(EXPORT_DIR, channel_name)
    if os.path.isdir(folder_path):
        for fname in os.listdir(folder_path):
            if fname.endswith(".json"):
                with open(os.path.join(folder_path, fname), "r", encoding="utf-8") as f:
                    messages.extend(json.load(f))

    if not messages:
        print(f"⚠️ No messages found for channel {channel_name}")
        return

    for msg in messages:
        sender = users_map.get(msg.get("user"), "Unknown User")
        text = msg.get("text", "")
        attachments = []

        # Files/images
        if "files" in msg:
            for fobj in msg["files"]:
                file_id = fobj.get("id")
                file_name = fobj.get("name") or fobj.get("title", "file")
                file_path = os.path.join(FILES_DIR, f"{file_id}_{file_name}")

                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        data = f.read()
                        attachment_id = models.execute_kw(
                            ODOO_DB, uid, ODOO_PASS,
                            "ir.attachment", "create",
                            [{
                                "name": file_name,
                                "datas": base64.b64encode(data).decode(),
                                "res_model": "mail.message",
                                "type": "binary",
                            }]
                        )
                        attachments.append(attachment_id)

        # Create Discuss message
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASS,
            "mail.message", "create",
            [{
                "model": "discuss.channel",
                "res_id": odoo_channel_id,
                "body": f"<b>{sender}:</b> {text}",
                "attachment_ids": [(6, 0, attachments)] if attachments else [],
                "message_type": "comment",
            }]
        )

    print(f"📨 Migrated {len(messages)} messages to {channel_name}")

# ========== START MIGRATION ==========
for ch_id, ch in channel_map.items():
    migrate_messages(ch_id, ch["name"])

print("🎉 Migration Completed! Now Discuss app has full chats with images & PDFs.")
