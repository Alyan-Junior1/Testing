# folder k structure dekhny k liye k folder ma kya kya ha 
import os

def print_directory_structure(root_dir, indent=""):
    try:
        items = os.listdir(root_dir)
    except PermissionError:
        print(indent + "[ACCESS DENIED]")
        return
    
    for i, item in enumerate(items):
        path = os.path.join(root_dir, item)
        is_last = (i == len(items) - 1)
        prefix = "└── " if is_last else "├── "

        if os.path.isdir(path):
            print(indent + prefix + " " + item)
            new_indent = indent + ("    " if is_last else "│   ")
            print_directory_structure(path, new_indent)
        else:
            print(indent + prefix + " " + item)

if __name__ == "__main__":
    folder_path = input("Enter folder path: ").strip()
    if os.path.exists(folder_path):
        print(f"Folder Structure of: {folder_path}\n")
        print_directory_structure(folder_path)
    else:
        print("❌ Folder path not found!")





# # ya check karta ha k kon kon se channel DM  folder k ander majood ha 
# import os, json

# root = r"real data"   # change to your folder path

# summary = {
#     "channels_file_found": False,
#     "channels_count": 0,
#     "per_channel_json_files": [],
#     "users_file": False,
#     "attachments_count": 0,
#     "attachments_examples": [],
#     "possible_dms": []
# }

# for entry in os.listdir(root):
#     p = os.path.join(root, entry)
#     if entry == "channels.json":
#         summary["channels_file_found"] = True
#     if entry == "users.json":
#         summary["users_file"] = True
#     if os.path.isdir(p):
#         # list per-channel jsons
#         for f in os.listdir(p):
#             if f.endswith(".json"):
#                 summary["per_channel_json_files"].append(os.path.join(entry, f))
#     if entry.startswith("downloaded_files"):
#         for f in os.listdir(p):
#             summary["attachments_count"] += 1
#             if len(summary["attachments_examples"]) < 6:
#                 summary["attachments_examples"].append(f)

# # attempt to detect DMs by scanning channels.json for "is_im" or "is_mpim"
# channels_json = os.path.join(root, "channels.json")
# if os.path.exists(channels_json):
#     try:
#         with open(channels_json, "r", encoding="utf-8") as fh:
#             data = json.load(fh)
#             if isinstance(data, list):
#                 summary["channels_count"] = len(data)
#                 for ch in data:
#                     if ch.get("is_im") or ch.get("is_mpim") or ch.get("is_private") and ch.get("member_count",0)<=2:
#                         summary["possible_dms"].append(ch.get("name") or ch.get("id"))
#     except Exception as e:
#         summary["channels_count"] = f"error reading file: {e}"

# print(json.dumps(summary, indent=2, ensure_ascii=False))




## is code ma ik issue ya ha k images open nahi ho rahi ha 
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
# # Helpers
# # ==============================
# def load_json(path):
#     with open(path, "r", encoding="utf-8") as f:
#         return json.load(f)

# def find_file(file_name, root, subfolders):
#     for sf in subfolders:
#         path = os.path.join(root, sf, file_name)
#         if os.path.exists(path):
#             return path
#     return None

# def create_channel(name):
#     ids = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'discuss.channel', 'search', [[['name', '=', name]]])
#     if ids:
#         return ids[0]
#     return models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'discuss.channel', 'create', [{'name': name}])

# def create_message(channel_id, body, author_id=None):
#     vals = {
#         'body': body,
#         'model': 'discuss.channel',
#         'res_id': channel_id,
#         'message_type': 'comment',
#     }
#     if author_id:
#         vals['author_id'] = author_id
#     return models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'mail.message', 'create', [vals])

# def create_attachment(file_path, message_id):
#     with open(file_path, "rb") as f:
#         file_bytes = f.read()
#     encoded = base64.b64encode(file_bytes).decode('utf-8')
#     mimetype, _ = mimetypes.guess_type(file_path)
#     attachment_id = models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS, 'ir.attachment', 'create',
#         [{
#             'name': os.path.basename(file_path),
#             'datas': encoded,
#             'res_model': 'mail.message',
#             'res_id': message_id,
#             'type': 'binary',
#             'mimetype': mimetype or 'application/octet-stream',
#         }]
#     )
#     models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'mail.message', 'write',
#                       [[message_id], {'attachment_ids': [(4, attachment_id)]}])
#     return attachment_id

# # ==============================
# # Main Migration
# # ==============================
# folder = input("Enter folder path: ").strip()
# FILES_SUBFOLDERS = ["files", "downloaded_files_api_fixed", "downloaded_files_api", "downloaded_files"]

# # Load users.json
# users_map = {}
# users_path = os.path.join(folder, "users.json")
# if os.path.exists(users_path):
#     users = load_json(users_path)
#     for u in users:
#         name = u.get("real_name") or u.get("name")
#         email = u.get("profile", {}).get("email")
#         partner_id = None
#         if email:
#             ids = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'res.partner', 'search', [[['email', '=', email]]], {'limit': 1})
#             if ids:
#                 partner_id = ids[0]
#             else:
#                 partner_id = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'res.partner', 'create',
#                                                [{'name': name, 'email': email}])
#         else:
#             partner_id = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'res.partner', 'create',
#                                            [{'name': name or "Slack User"}])
#         users_map[u["id"]] = partner_id

# # Process JSON files
# for file in os.listdir(folder):
#     if not file.endswith(".json") or file == "users.json":
#         continue
#     path = os.path.join(folder, file)
#     messages = load_json(path)

#     if file.startswith("dm_"):
#         channel_name = file.replace("dm_", "").replace(".json", "")
#     else:
#         channel_name = file.replace(".json", "")

#     print(f"📌 Migrating Channel: {channel_name}")
#     channel_id = create_channel(channel_name)

#     for msg in messages:
#         text = msg.get("text", "")
#         user = msg.get("user")
#         author_id = users_map.get(user)
#         body = text or "(no text)"

#         # include blocks/attachments text if present
#         if msg.get("blocks"):
#             for b in msg["blocks"]:
#                 for e in b.get("elements", []):
#                     for t in e.get("elements", []):
#                         if t.get("text"):
#                             body += "\n" + t["text"]

#         message_id = create_message(channel_id, body, author_id)
#         print(f"➡️ Message imported (id={message_id})")

#         files = msg.get("files", [])
#         for f in files:
#             if isinstance(f, dict):
#                 fname = f.get("name") or f.get("id")
#             elif isinstance(f, str):
#                 fname = f
#             else:
#                 continue
#             file_path = find_file(fname, folder, FILES_SUBFOLDERS)
#             if file_path:
#                 create_attachment(file_path, message_id)
#                 print(f"📎 Attached: {file_path}")

# print("✅ Migration completed successfully!")






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
# # Helpers
# # ==============================
# def load_json(path):
#     with open(path, "r", encoding="utf-8") as f:
#         return json.load(f)

# def find_file(file_name, root, subfolders):
#     for sf in subfolders:
#         path = os.path.join(root, sf, file_name)
#         if os.path.exists(path):
#             return path
#     return None

# def create_channel(name):
#     ids = models.execute_kw(ODOO_DB, uid, ODOO_PASS,
#                             'discuss.channel', 'search',
#                             [[['name', '=', name]]])
#     if ids:
#         return ids[0]
#     return models.execute_kw(ODOO_DB, uid, ODOO_PASS,
#                              'discuss.channel', 'create',
#                              [{'name': name}])

# def create_message(channel_id, body, author_id=None):
#     vals = {
#         'body': body,
#         'model': 'discuss.channel',
#         'res_id': channel_id,
#         'message_type': 'comment',
#     }
#     if author_id:
#         vals['author_id'] = author_id
#     return models.execute_kw(ODOO_DB, uid, ODOO_PASS,
#                              'mail.message', 'create', [vals])


# def create_attachment(file_path, message_id):
#     """Upload file as ir.attachment and embed in message body."""
#     with open(file_path, "rb") as f:
#         file_bytes = f.read()
#     encoded = base64.b64encode(file_bytes).decode('utf-8')
#     mimetype, _ = mimetypes.guess_type(file_path)

#     # Create attachment
#     attachment_id = models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS, 'ir.attachment', 'create',
#         [{
#             'name': os.path.basename(file_path),
#             'datas': encoded,
#             'res_model': 'mail.message',
#             'res_id': message_id,
#             'type': 'binary',
#             'mimetype': mimetype or 'application/octet-stream',
#         }]
#     )

#     # Generate correct HTML for Discuss app
#     if mimetype and mimetype.startswith("image/"):
#         # Use field=datas&download=false to show inline image
#         html = f"""<p>
# <img src="/web/content/{attachment_id}?model=mail.message&field=datas&download=false" 
# alt="{os.path.basename(file_path)}" style="max-width:400px;"/>
# </p>"""
#     else:
#         # Downloadable link for other files
#         html = f"""<p>
# <a href="/web/content/{attachment_id}?download=true">{os.path.basename(file_path)}</a>
# </p>"""

#     # Update message body and attach the attachment properly
#     models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS,
#         'mail.message', 'write',
#         [[message_id], {'body': html,
#                         'attachment_ids': [(4, attachment_id, 0)]}]
#     )

#     return attachment_id


# # ==============================
# # Main Migration
# # ==============================
# folder = input("Enter folder path: ").strip()
# FILES_SUBFOLDERS = ["files", "downloaded_files_api_fixed",
#                     "downloaded_files_api", "downloaded_files"]

# # Load users.json if exists
# users_map = {}
# users_path = os.path.join(folder, "users.json")
# if os.path.exists(users_path):
#     users = load_json(users_path)
#     for u in users:
#         name = u.get("real_name") or u.get("name")
#         email = u.get("profile", {}).get("email")
#         partner_id = None
#         if email:
#             ids = models.execute_kw(
#                 ODOO_DB, uid, ODOO_PASS, 'res.partner',
#                 'search', [[['email', '=', email]]], {'limit': 1})
#             if ids:
#                 partner_id = ids[0]
#             else:
#                 partner_id = models.execute_kw(
#                     ODOO_DB, uid, ODOO_PASS, 'res.partner',
#                     'create', [{'name': name, 'email': email}])
#         else:
#             partner_id = models.execute_kw(
#                 ODOO_DB, uid, ODOO_PASS, 'res.partner',
#                 'create', [{'name': name or "Slack User"}])
#         users_map[u["id"]] = partner_id

# # Process JSON files
# for file in os.listdir(folder):
#     if not file.endswith(".json") or file == "users.json":
#         continue
#     path = os.path.join(folder, file)
#     messages = load_json(path)

#     if file.startswith("dm_"):
#         channel_name = file.replace("dm_", "").replace(".json", "")
#     else:
#         channel_name = file.replace(".json", "")

#     print(f"\n📌 Migrating Channel: {channel_name}")
#     channel_id = create_channel(channel_name)

#     for msg in messages:
#         text = msg.get("text", "")
#         user = msg.get("user")
#         author_id = users_map.get(user)
#         body = text or "(no text)"

#         # include blocks/attachments text if present
#         if msg.get("blocks"):
#             for b in msg["blocks"]:
#                 for e in b.get("elements", []):
#                     for t in e.get("elements", []):
#                         if t.get("text"):
#                             body += "\n" + t["text"]

#         message_id = create_message(channel_id, body, author_id)
#         print(f"➡️ Message imported (id={message_id})")

#         files = msg.get("files", [])
#         for f in files:
#             if isinstance(f, dict):
#                 fname = f.get("name") or f.get("id")
#             elif isinstance(f, str):
#                 fname = f
#             else:
#                 continue
#             file_path = find_file(fname, folder, FILES_SUBFOLDERS)
#             if file_path:
#                 try:
#                     create_attachment(file_path, message_id)
#                     print(f"📎 Attached & Embedded: {file_path}")
#                 except Exception as e:
#                     print(f"❌ Error attaching {file_path}: {e}")

# print("\n✅ Migration completed successfully!")



# import os
# import json
# import base64
# import mimetypes
# import xmlrpc.client
# import tkinter as tk
# from tkinter import filedialog, ttk, messagebox

# # ==============================
# # Odoo Connection Settings
# # ==============================
# ODOO_URL = "http://localhost:8069"
# ODOO_DB = "odoo19db"
# ODOO_USER = "admin"
# ODOO_PASS = "admin123"

# # ==============================
# # Helper Functions
# # ==============================
# def connect_odoo():
#     try:
#         common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
#         uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
#         models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
#         return uid, models
#     except Exception as e:
#         messagebox.showerror("Odoo Connection Error", str(e))
#         return None, None

# def load_json(path):
#     with open(path, "r", encoding="utf-8") as f:
#         return json.load(f)

# def find_file(file_name, root, subfolders):
#     for sf in subfolders:
#         path = os.path.join(root, sf, file_name)
#         if os.path.exists(path):
#             return path
#     return None

# def create_channel(models, uid, name):
#     ids = models.execute_kw(ODOO_DB, uid, ODOO_PASS,
#                             'discuss.channel', 'search',
#                             [[['name', '=', name]]])
#     if ids:
#         return ids[0]
#     return models.execute_kw(ODOO_DB, uid, ODOO_PASS,
#                              'discuss.channel', 'create',
#                              [{'name': name}])

# def create_message(models, uid, channel_id, body, author_id=None):
#     vals = {
#         'body': body,
#         'model': 'discuss.channel',
#         'res_id': channel_id,
#         'message_type': 'comment',
#     }
#     if author_id:
#         vals['author_id'] = author_id
#     return models.execute_kw(ODOO_DB, uid, ODOO_PASS,
#                              'mail.message', 'create', [vals])

# def create_attachment(models, uid, file_path, message_id):
#     # Read file and encode
#     with open(file_path, "rb") as f:
#         file_bytes = f.read()
#     encoded = base64.b64encode(file_bytes).decode('utf-8')
#     mimetype, _ = mimetypes.guess_type(file_path)

#     # Create attachment linked to mail.message
#     attachment_id = models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS, 'ir.attachment', 'create',
#         [{
#             'name': os.path.basename(file_path),
#             'datas': encoded,
#             'res_model': 'mail.message',
#             'res_id': message_id,
#             'type': 'binary',
#             'mimetype': mimetype or 'application/octet-stream',
#         }]
#     )

#     # Update message body with inline image or file link
#     if mimetype and mimetype.startswith("image/"):
#         html = f"""<p>
#         <img src="/web/content/{attachment_id}?model=mail.message&field=datas&download=false" 
#         alt="{os.path.basename(file_path)}" style="max-width:400px;"/>
#         </p>"""
#     else:
#         html = f"""<p><a href="/web/content/{attachment_id}?download=true" target="_blank">
#         {os.path.basename(file_path)}</a></p>"""

#     models.execute_kw(
#         ODOO_DB, uid, ODOO_PASS,
#         'mail.message', 'write',
#         [[message_id], {'body': html,
#                         'attachment_ids': [(4, attachment_id)]}]
#     )

#     return attachment_id


# # ==============================
# # Main Migration Function
# # ==============================
# def migrate(folder_path, progress):
#     uid, models = connect_odoo()
#     if not uid:
#         return

#     FILES_SUBFOLDERS = ["files", "downloaded_files_api_fixed",
#                         "downloaded_files_api", "downloaded_files"]

#     # Users
#     users_map = {}
#     users_path = os.path.join(folder_path, "users.json")
#     if os.path.exists(users_path):
#         users = load_json(users_path)
#         for u in users:
#             name = u.get("real_name") or u.get("name") or "Slack User"
#             email = u.get("profile", {}).get("email")
#             partner_id = None
#             if email:
#                 ids = models.execute_kw(
#                     ODOO_DB, uid, ODOO_PASS, 'res.partner',
#                     'search', [[['email', '=', email]]], {'limit': 1})
#                 if ids:
#                     partner_id = ids[0]
#                 else:
#                     partner_id = models.execute_kw(
#                         ODOO_DB, uid, ODOO_PASS, 'res.partner',
#                         'create', [{'name': name, 'email': email}])
#             else:
#                 partner_id = models.execute_kw(
#                     ODOO_DB, uid, ODOO_PASS, 'res.partner',
#                     'create', [{'name': name}])
#             users_map[u["id"]] = partner_id

#     json_files = [f for f in os.listdir(folder_path) if f.endswith(".json") and f != "users.json"]
#     total = len(json_files)
#     progress['maximum'] = total
#     progress['value'] = 0

#     for idx, file in enumerate(json_files):
#         path = os.path.join(folder_path, file)
#         messages = load_json(path)

#         channel_name = file.replace("dm_", "").replace(".json", "")
#         channel_id = create_channel(models, uid, channel_name)

#         for msg in messages:
#             text = msg.get("text", "")
#             user = msg.get("user")
#             author_id = users_map.get(user)
#             body = text or "(no text)"

#             if msg.get("blocks"):
#                 for b in msg["blocks"]:
#                     for e in b.get("elements", []):
#                         for t in e.get("elements", []):
#                             if t.get("text"):
#                                 body += "\n" + t["text"]

#             message_id = create_message(models, uid, channel_id, body, author_id)

#             files = msg.get("files", [])
#             for f in files:
#                 if isinstance(f, dict):
#                     fname = f.get("name") or f.get("id")
#                 elif isinstance(f, str):
#                     fname = f
#                 else:
#                     continue
#                 file_path = find_file(fname, folder_path, FILES_SUBFOLDERS)
#                 if file_path:
#                     try:
#                         create_attachment(models, uid, file_path, message_id)
#                     except Exception as e:
#                         print(f"Error attaching {file_path}: {e}")

#         progress['value'] = idx + 1
#         root.update_idletasks()

#     messagebox.showinfo("Migration Completed", "✅ All channels and files migrated successfully!")

# # ==============================
# # Tkinter GUI
# # ==============================
# root = tk.Tk()
# root.title("Slack to Odoo Migration")

# frame = tk.Frame(root, padx=10, pady=10)
# frame.pack()

# folder_label = tk.Label(frame, text="Select Slack Export Folder:")
# folder_label.pack(anchor="w")

# folder_path_var = tk.StringVar()
# folder_entry = tk.Entry(frame, textvariable=folder_path_var, width=60)
# folder_entry.pack(side="left", padx=(0,10))

# def browse_folder():
#     folder = filedialog.askdirectory()
#     if folder:
#         folder_path_var.set(folder)

# browse_btn = tk.Button(frame, text="Browse", command=browse_folder)
# browse_btn.pack(side="left")

# progress = ttk.Progressbar(root, length=500, mode='determinate')
# progress.pack(pady=10)

# def start_migration():
#     folder = folder_path_var.get()
#     if not folder or not os.path.exists(folder):
#         messagebox.showerror("Error", "Please select a valid folder!")
#         return
#     migrate(folder, progress)

# start_btn = tk.Button(root, text="Start Migration", command=start_migration, bg="green", fg="white")
# start_btn.pack(pady=5)

# root.mainloop()
