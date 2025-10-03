# import os
# import zipfile
# import json
# import base64
# import mimetypes
# import xmlrpc.client

# # ---------------- Odoo Config ----------------
# URL = "http://localhost:8069"
# DB = "odoo19db"
# USERNAME = "admin"
# PASSWORD = "admin123"

# # Slack export zip file
# SLACK_ZIP = "Odoo Testing Slack export Sep 22 2025 - Sep 23 2025.zip"

# # ---------------- Odoo Connection ----------------
# common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
# uid = common.authenticate(DB, USERNAME, PASSWORD, {})
# if not uid:
#     raise Exception("❌ Authentication failed")

# models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
# print(f"✅ Connected to Odoo as UID: {uid}")

# # ---------------- Extract Slack Data ----------------
# extract_dir = "slack_to_odoo_import"
# if os.path.exists(extract_dir):
#     import shutil
#     shutil.rmtree(extract_dir)

# with zipfile.ZipFile(SLACK_ZIP, "r") as z:
#     z.extractall(extract_dir)
# print(f"✅ Extracted to {extract_dir}")

# # ---------------- Load Slack Users ----------------
# users_file = os.path.join(extract_dir, "users.json")
# slack_users = {}
# if os.path.exists(users_file):
#     with open(users_file, "r", encoding="utf-8") as f:
#         for user in json.load(f):
#             slack_users[user["id"]] = user.get("real_name", user.get("name"))
# print(f"✅ Loaded {len(slack_users)} Slack users")

# # ---------------- Helper: Create Discuss Channel ----------------
# def get_or_create_channel(name):
#     existing = models.execute_kw(DB, uid, PASSWORD,
#         "discuss.channel", "search_read",
#         [[["name", "=", name]]], {"fields": ["id"], "limit": 1})
#     if existing:
#         return existing[0]["id"]
#     channel_id = models.execute_kw(DB, uid, PASSWORD,
#         "discuss.channel", "create",
#         [{"name": name, "channel_type": "channel"}])
#     print(f"📢 Created channel: {name}")
#     return channel_id

# # ---------------- Helper: Post message in Discuss ----------------
# def create_message(channel_id, author_id, body):
#     models.execute_kw(DB, uid, PASSWORD,
#         "mail.message", "create", [{
#             "model": "discuss.channel",
#             "res_id": channel_id,
#             "body": body,
#             "message_type": "comment",
#             "subtype_id": 1,
#             "author_id": author_id,
#         }])

# # ---------------- Helper: Upload file into Documents ----------------
# def upload_file(filepath, slack_user_id=None):
#     filename = os.path.basename(filepath)
#     mimetype, _ = mimetypes.guess_type(filename)
#     if not mimetype:
#         mimetype = "application/octet-stream"

#     with open(filepath, "rb") as f:
#         data = f.read()

#     doc_id = models.execute_kw(DB, uid, PASSWORD,
#         "documents.document", "create", [{
#             "name": filename,
#             "datas": base64.b64encode(data).decode(),
#             "mimetype": mimetype,
#             "owner_id": uid,
#         }])
#     print(f"📄 Uploaded document: {filename}")
#     return doc_id

# # ---------------- Process Slack Channels ----------------
# for channel in os.listdir(extract_dir):
#     channel_path = os.path.join(extract_dir, channel)
#     if not os.path.isdir(channel_path):
#         continue

#     channel_id = get_or_create_channel(channel)

#     total_msgs = 0
#     for file in os.listdir(channel_path):
#         if not file.endswith(".json"):
#             continue
#         with open(os.path.join(channel_path, file), "r", encoding="utf-8") as f:
#             messages = json.load(f)

#         for msg in messages:
#             text = msg.get("text", "")
#             slack_uid = msg.get("user")
#             author_name = slack_users.get(slack_uid, "Slack User")
#             # Find Odoo partner for author
#             partner = models.execute_kw(DB, uid, PASSWORD,
#                 "res.partner", "search_read",
#                 [[["name", "=", author_name]]], {"fields": ["id"], "limit": 1})
#             author_id = partner[0]["id"] if partner else False

#             if text:
#                 create_message(channel_id, author_id, text)
#                 total_msgs += 1

#             # Handle files
#             if "files" in msg:
#                 for fdata in msg["files"]:
#                     fname = fdata.get("name", "slack_file")
#                     # Try to find exported file in Slack zip
#                     fpath = os.path.join(channel_path, fname)
#                     if os.path.exists(fpath):
#                         upload_file(fpath, slack_uid)
#                     else:
#                         print(f"⚠️ File not found in export: {fname}")

#     print(f"✅ Imported {total_msgs} messages into {channel}")

# print("🎉 Migration complete! Check Odoo Discuss & Documents apps.")

