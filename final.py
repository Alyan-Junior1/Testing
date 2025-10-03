# # ya bilkul sahi chal raha ha discuss app ma images b le kar aa raha ha likn images open nahi ho rhi
# import os
# import base64
# import requests
# import xmlrpc.client
# import mimetypes

# # ==============================
# # Odoo Connection
# # ==============================
# ODOO_URL = "http://localhost:8069"
# ODOO_DB = "odoo19db"
# ODOO_USER = "admin"
# ODOO_PASS = "admin123"

# # Connect Odoo
# common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
# uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
# models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

# print(f"✅ Connected to Odoo as UID: {uid}")

# # ==============================
# # Slack Tokens
# # ==============================
# USER_TOKEN = "YOUR_SLACK_TOKEN"
# BOT_TOKEN = "YOUR_SLACK_TOKEN"

# HEADERS_USER = {"Authorization": f"Bearer {USER_TOKEN}"}
# HEADERS_BOT = {"Authorization": f"Bearer {BOT_TOKEN}"}

# # ==============================
# # Helper Functions
# # ==============================
# def slack_api(method, headers, params=None):
#     url = f"https://slack.com/api/{method}"
#     resp = requests.get(url, headers=headers, params=params)
#     return resp.json()

# def download_file(url, headers):
#     resp = requests.get(url, headers=headers, stream=True)
#     if resp.status_code == 200:
#         return resp.content
#     return None

# def create_attachment(file_bytes, file_name, res_model="discuss.channel", res_id=False):
#     """Upload file to Odoo Documents with proper mimetype"""
#     encoded = base64.b64encode(file_bytes).decode("utf-8")
#     mimetype, _ = mimetypes.guess_type(file_name)  # detect mime e.g. image/png, application/pdf
    
#     attachment_id = models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS,
#         'ir.attachment', 'create',
#         [{
#             'name': file_name,
#             'datas': encoded,
#             'res_model': res_model,
#             'res_id': res_id or 0,
#             'type': 'binary',
#             'mimetype': mimetype or 'application/octet-stream',
#         }]
#     )
#     return attachment_id

# # def create_attachment(file_bytes, file_name, res_model="discuss.channel", res_id=False):
# #     """Upload file to Odoo Documents"""
# #     encoded = base64.b64encode(file_bytes).decode("utf-8")
# #     attachment_id = models.execute_kw(
# #         ODOO_DB, uid, ODOO_PASS,
# #         'ir.attachment', 'create',
# #         [{
# #             'name': file_name,
# #             'datas': encoded,
# #             'res_model': res_model,
# #             'res_id': res_id or 0,
# #             'type': 'binary',
# #         }]
# #     )
# #     return attachment_id

# def create_message(channel_id, body, attachment_id=None):
#     """Create message in Odoo Discuss"""
#     vals = {
#         'body': body,
#         'model': 'discuss.channel',
#         'res_id': channel_id,
#         'message_type': 'comment',
#     }
#     if attachment_id:
#         vals['attachment_ids'] = [(4, attachment_id)]
#     models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS,
#         'mail.message', 'create', [vals]
#     )

# # ==============================
# # Migration Process
# # ==============================
# channels = slack_api("conversations.list", HEADERS_USER).get("channels", [])
# print(f"🔹 Found {len(channels)} channels")

# for ch in channels:
#     channel_name = ch["name"]
#     channel_id = ch["id"]
#     print(f"\n📌 Migrating Channel: {channel_name} ({channel_id})")

#     # Create/find channel in Odoo
#     odoo_channel_id = models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS,
#         'discuss.channel', 'create',
#         [{'name': channel_name}],
#     )

#     # Fetch messages
#     msgs = slack_api("conversations.history", HEADERS_USER, {"channel": channel_id}).get("messages", [])
#     print(f"   ✅ {len(msgs)} messages fetched")

#     for msg in msgs:
#         text = msg.get("text", "")
#         files = msg.get("files", [])

#         if files:
#             for f in files:
#                 file_url = f.get("url_private")
#                 file_name = f.get("name")
#                 file_bytes = download_file(file_url, HEADERS_BOT)

#                 if file_bytes:
#                     try:
#                         att_id = create_attachment(file_bytes, file_name, "discuss.channel", odoo_channel_id)
#                         create_message(odoo_channel_id, text or f"📎 {file_name}", att_id)
#                         print(f"      📂 File Uploaded: {file_name}")
#                     except Exception as e:
#                         print(f"      ❌ Error uploading {file_name}: {e}")
#         else:
#             # Normal message
#             create_message(odoo_channel_id, text)
#             print(f"      💬 Message Migrated: {text[:30]}...")

# print("\n✅ Migration Completed Successfully!")



# ya code b kaam kar raha ha images b open ho rhai ha likn in k channel k name nahi id show ho rahi ha 
# import os
# import json
# import base64
# import mimetypes
# import xmlrpc.client

# # ==============================
# # Odoo Connection
# # ==============================
# ODOO_URL = "http://localhost:8069"
# ODOO_DB = "odoo19db"
# ODOO_USER = "admin"
# ODOO_PASS = "admin123"

# common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
# uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
# models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
# print(f"✅ Connected to Odoo as UID: {uid}")

# # ==============================
# # Slack export folder
# # ==============================
# SLACK_ROOT = r"slack_export"
# FILES_FOLDER = os.path.join(SLACK_ROOT, "files")

# # ==============================
# # Helper functions
# # ==============================
# def create_channel(name):
#     """Create Odoo Discuss channel"""
#     return models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS,
#         'discuss.channel', 'create', [{'name': name}]
#     )

# def create_message(channel_id, body=""):
#     """Create mail.message in Discuss and return ID"""
#     message_id = models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS,
#         'mail.message', 'create',
#         [{
#             'body': body,
#             'model': 'discuss.channel',
#             'res_id': channel_id,
#             'message_type': 'comment',
#         }]
#     )
#     return message_id

# def create_attachment(file_path, message_id):
#     """Upload file as ir.attachment linked to mail.message"""
#     with open(file_path, "rb") as f:
#         file_bytes = f.read()
#     encoded = base64.b64encode(file_bytes).decode('utf-8')
#     mimetype, _ = mimetypes.guess_type(file_path)

#     attachment_id = models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS,
#         'ir.attachment', 'create',
#         [{
#             'name': os.path.basename(file_path),
#             'datas': encoded,
#             'res_model': 'mail.message',
#             'res_id': message_id,
#             'type': 'binary',
#             'mimetype': mimetype or 'application/octet-stream',
#         }]
#     )
#     # Link attachment to message
#     models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS,
#         'mail.message', 'write',
#         [[message_id], {'attachment_ids': [(4, attachment_id)]}]
#     )
#     return attachment_id

# def load_json(file_path):
#     with open(file_path, "r", encoding="utf-8") as f:
#         return json.load(f)

# # ==============================
# # Migration Process
# # ==============================
# # Get all channel JSON files
# channel_files = [
#     f for f in os.listdir(SLACK_ROOT)
#     if f.startswith("user_channel_") or f.startswith("bot_channel_")
# ]

# for ch_file in channel_files:
#     ch_path = os.path.join(SLACK_ROOT, ch_file)
#     messages = load_json(ch_path)

#     # Use filename as channel name
#     channel_name = ch_file.replace(".json", "")
#     print(f"\n📌 Migrating Channel: {channel_name}")

#     odoo_channel_id = create_channel(channel_name)

#     for msg in messages:
#         text = msg.get("text", "")
#         files_list = msg.get("files", [])

#         # Step 1: Create message
#         message_id = create_message(odoo_channel_id, text or "📎 File attached")

#         # Step 2: Attach files if exist
#         for f in files_list:
#             file_name = f.get("name")
#             slack_file_id = f.get("id")
#             local_file_path = os.path.join(FILES_FOLDER, f"{slack_file_id}_{file_name}")

#             if os.path.exists(local_file_path):
#                 try:
#                     create_attachment(local_file_path, message_id)
#                     print(f"      🖼 File Uploaded: {file_name}")
#                 except Exception as e:
#                     print(f"      ❌ Error uploading {file_name}: {e}")

#         if not files_list:
#             print(f"      💬 Message Migrated: {text[:30]}...")

# print("\n✅ Migration Completed! All messages and files are in Discuss.")





