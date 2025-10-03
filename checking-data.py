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

# common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
# uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
# models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

# print(f"✅ Connected to Odoo as UID: {uid}")

# # ==============================
# # Helper Functions
# # ==============================
# def create_discuss_channel(name="Test Channel"):
#     return models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS,
#         'discuss.channel', 'create', [{'name': name}]
#     )

# def create_message(channel_id, body="Test message"):
#     return models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS,
#         'mail.message', 'create',
#         [{
#             'body': body,
#             'model': 'discuss.channel',
#             'res_id': channel_id,
#             'message_type': 'comment',
#         }]
#     )

# def create_attachment(file_path, message_id):
#     with open(file_path, "rb") as f:
#         file_bytes = f.read()
#     encoded = base64.b64encode(file_bytes).decode('utf-8')
#     mimetype, _ = mimetypes.guess_type(file_path)
#     attachment_id = models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS,
#         'ir.attachment', 'create',
#         [{
#             'name': file_path.split("/")[-1],
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

# # ==============================
# # Test Process
# # ==============================
# channel_id = create_discuss_channel("Image Test Channel")
# print(f"📌 Created test channel with ID: {channel_id}")

# message_id = create_message(channel_id, "Here is a test image!")
# print(f"💬 Created test message with ID: {message_id}")

# # Replace with your local image path
# image_path = "sample.png"
# attachment_id = create_attachment(image_path, message_id)
# print(f"🖼 Uploaded image with attachment ID: {attachment_id}")

# print("\n✅ Test completed! Open Discuss app and check the image.")




import xmlrpc.client

ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo19db"
ODOO_USER = "admin"
ODOO_PASS = "admin123"

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
print("UID:", uid)

