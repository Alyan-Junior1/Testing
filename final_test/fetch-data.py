import os
import json
import requests
from datetime import datetime
import xmlrpc.client
import base64

# -----------------------
# CONFIGURATION
# -----------------------
SLACK_FOLDER = "slack_data/channels"
FILES_FOLDER = "odoo_import/attachments"
SLACK_TOKEN = "YOUR_SLACK_TOKEN"

ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo19db"
ODOO_USER = "admin"
ODOO_PASSWORD = "admin123"

# -----------------------
# ODOO CONNECTION
# -----------------------
common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

# -----------------------
# HELPERS
# -----------------------
def slack_ts_to_datetime(ts):
    return datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M:%S")

def download_file(url, filename):
    headers = {"Authorization": f"Bearer {SLACK_TOKEN}"}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        file_path = os.path.join(FILES_FOLDER, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return file_path
    else:
        print(f"Failed to download {filename} from {url}")
        return None

def get_or_create_user(slack_user):
    user_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                                 'res.users', 'search', [[['login', '=', slack_user]]])
    if user_ids:
        return user_ids[0]
    user_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                                'res.users', 'create', [{'name': slack_user, 'login': slack_user}])
    return user_id

def get_or_create_channel(channel_name):
    channel_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                                    'discuss.channel', 'search', [[['name', '=', channel_name]]])
    if channel_ids:
        return channel_ids[0]
    channel_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                                   'discuss.channel', 'create', [{'name': channel_name}])
    return channel_id

def post_message(channel_id, author_id, message, attachments=None):
    # Create message via message_post
    attachment_ids = []
    if attachments:
        for filepath in attachments:
            with open(filepath, "rb") as f:
                data = base64.b64encode(f.read()).decode('utf-8')
            att_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                                       'ir.attachment', 'create', [{
                                           'name': os.path.basename(filepath),
                                           'datas': data,
                                           'res_model': 'mail.message',
                                           'res_id': 0,  # We'll attach after posting
                                       }])
            attachment_ids.append(att_id)

    msg_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                               'mail.message', 'create', [{
                                   'channel_id': channel_id,
                                   'author_id': author_id,
                                   'body': message,
                               }])

    # Link attachments to message
    for att_id in attachment_ids:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                          'ir.attachment', 'write', [[att_id], {'res_model': 'mail.message', 'res_id': msg_id}])

    return msg_id

# -----------------------
# PROCESS SLACK DATA
# -----------------------
for channel_name in os.listdir(SLACK_FOLDER):
    channel_path = os.path.join(SLACK_FOLDER, channel_name)
    messages_file = os.path.join(channel_path, "messages.json")

    if os.path.isfile(messages_file):
        print(f"Processing channel: {channel_name}")
        with open(messages_file, "r", encoding="utf-8") as f:
            messages = json.load(f)

        channel_id = get_or_create_channel(channel_name)

        for msg in messages:
            author = msg.get("user", msg.get("username", "Unknown"))
            author_id = get_or_create_user(author)
            text = msg.get("text", "")
            attachments_paths = []

            if "files" in msg:
                for f in msg["files"]:
                    filename = f.get("name", "unknown_file")
                    url = f.get("url_private")
                    if url:
                        local_path = download_file(url, filename)
                        if local_path:
                            attachments_paths.append(local_path)

            post_message(channel_id, author_id, text, attachments_paths)

print("Slack migration to Odoo Discuss completed successfully!")
