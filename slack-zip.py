# khud se data create kar k upload kar rhe ha odoo ma aur sahi se ho raha ha 
# import xmlrpc.client
# import base64

# # ---- Odoo connection ----
# url = "http://localhost:8069"   # apna url lagao
# db = "odoo19db"                 # apna DB lagao
# username = "admin"              # apna user lagao
# password = "admin123"              # apna password lagao

# # ---- Connect ----
# common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
# uid = common.authenticate(db, username, password, {})
# models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# print(f"✅ Connected to Odoo as UID {uid}")

# # ---- 1. Test channel in Discuss ----
# channel_id = models.execute_kw(db, uid, password, 'discuss.channel', 'create', [{
#     'name': 'Test Slack Channel',
#     'channel_partner_ids': [(4, uid)],  # add current user as member
# }])
# print(f"💬 Created Discuss channel ID: {channel_id}")

# # ---- 2. Upload a PDF to Documents ----
# pdf_path = "sample.pdf"   # apne system me ek test pdf file rakho isi naam se
# with open(pdf_path, "rb") as f:
#     pdf_data = base64.b64encode(f.read()).decode()

# doc_id = models.execute_kw(db, uid, password, 'documents.document', 'create', [{
#     'name': 'Sample PDF',
#     'datas': pdf_data,
#     'mimetype': 'application/pdf',
# }])
# print(f"📄 Uploaded PDF to Documents ID: {doc_id}")

# # ---- 3. Upload an Image to Knowledge ----
# img_path = "sample.png"   # apne system me ek test image rakho isi naam se
# with open(img_path, "rb") as f:
#     img_data = base64.b64encode(f.read()).decode()

# attachment_id = models.execute_kw(db, uid, password, 'ir.attachment', 'create', [{
#     'name': 'Sample Image',
#     'datas': img_data,
#     'mimetype': 'image/png',
#     'res_model': 'knowledge.article',
# }])

# article_id = models.execute_kw(db, uid, password, 'knowledge.article', 'create', [{
#     'name': 'Slack Migration Test Article',
#     'body': '<p>Here is an image from Slack:</p><img src="/web/image/%d" />' % attachment_id,
# }])
# print(f"📘 Created Knowledge Article ID: {article_id} with image attachment")

