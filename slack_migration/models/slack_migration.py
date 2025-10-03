import os
import json
import base64
import mimetypes
from odoo import models, api, fields, _

class SlackMigration(models.Model):
    _name = "slack.migration"
    _description = "Slack Data Migration"

    name = fields.Char("Name")

    @api.model
    def migrate_folder(self, folder_path):
        FILES_SUBFOLDERS = ["files", "downloaded_files_api_fixed",
                            "downloaded_files_api", "downloaded_files"]

        users_map = {}
        users_path = os.path.join(folder_path, "users.json")
        if os.path.exists(users_path):
            with open(users_path, "r", encoding="utf-8") as f:
                users = json.load(f)
            for u in users:
                name = u.get("real_name") or u.get("name") or "Slack User"
                email = u.get("profile", {}).get("email")
                partner = None
                if email:
                    partner = self.env['res.partner'].search([('email', '=', email)], limit=1)
                if not partner:
                    partner = self.env['res.partner'].create({'name': name, 'email': email})
                users_map[u["id"]] = partner.id

        for file in os.listdir(folder_path):
            if not file.endswith(".json") or file == "users.json":
                continue
            path = os.path.join(folder_path, file)
            with open(path, "r", encoding="utf-8") as f:
                messages = json.load(f)

            if file.startswith("dm_"):
                channel_name = file.replace("dm_", "").replace(".json", "")
            else:
                channel_name = file.replace(".json", "")

            channel = self.env['discuss.channel'].search([('name', '=', channel_name)], limit=1)
            if not channel:
                channel = self.env['discuss.channel'].create({'name': channel_name})

            for msg in messages:
                text = msg.get("text", "")
                user_id = msg.get("user")
                partner_id = users_map.get(user_id)
                body = text or "(no text)"

                # include blocks text if present
                if msg.get("blocks"):
                    for b in msg["blocks"]:
                        for e in b.get("elements", []):
                            for t in e.get("elements", []):
                                if t.get("text"):
                                    body += "\n" + t["text"]

                message = self.env['mail.message'].create({
                    'body': body,
                    'model': 'discuss.channel',
                    'res_id': channel.id,
                    'message_type': 'comment',
                    'author_id': partner_id,
                })

                files = msg.get("files", [])
                for f in files:
                    if isinstance(f, dict):
                        fname = f.get("name") or f.get("id")
                    elif isinstance(f, str):
                        fname = f
                    else:
                        continue

                    # Search in possible subfolders
                    file_path = None
                    for sf in FILES_SUBFOLDERS:
                        temp_path = os.path.join(folder_path, sf, fname)
                        if os.path.exists(temp_path):
                            file_path = temp_path
                            break

                    if file_path:
                        self.create_attachment(file_path, message)

    def create_attachment(self, file_path, message):
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        encoded = base64.b64encode(file_bytes)
        mimetype, _ = mimetypes.guess_type(file_path)
        attachment = self.env['ir.attachment'].create({
            'name': os.path.basename(file_path),
            'datas': encoded,
            'res_model': 'mail.message',
            'res_id': message.id,
            'type': 'binary',
            'mimetype': mimetype or 'application/octet-stream',
        })

        # Correct HTML embedding for Discuss
        if mimetype and mimetype.startswith("image/"):
            html = f"""<p>
<img src="/web/content/{attachment.id}?model=mail.message&field=datas&download=false"
alt="{os.path.basename(file_path)}" style="max-width:400px;"/>
</p>"""
        else:
            html = f"""<p>
<a href="/web/content/{attachment.id}?download=true">{os.path.basename(file_path)}</a>
</p>"""

        message.write({'body': html, 'attachment_ids': [(4, attachment.id)]})
