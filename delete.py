import xmlrpc.client

ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo19db"
ODOO_USER = "admin"
ODOO_PASS = "admin123"

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

# 🔎 Saare discuss channels fetch karo
channels = models.execute_kw(
    ODOO_DB, uid, ODOO_PASS,
    'discuss.channel', 'search_read',
    [[]],
    {'fields': ['id', 'name', 'channel_type']}
)

# 🚫 System channels jo delete nahi honay chahiye
PROTECTED_CHANNELS = ["General", "general", "Whole Company"]

to_delete = []
for c in channels:
    name = c['name']
    ctype = c['channel_type']

    if name in PROTECTED_CHANNELS:
        print(f"⏩ Skipping protected system channel: {name}")
        continue

    if ctype in ["channel", "chat"]:
        to_delete.append(c['id'])
        print(f"🗑 Queued for delete: {name} (id={c['id']})")

if to_delete:
    models.execute_kw(
        ODOO_DB, uid, ODOO_PASS,
        'discuss.channel', 'unlink', [to_delete]
    )
    print(f"✅ Deleted {len(to_delete)} custom channels")
else:
    print("ℹ️ No custom channels found to delete")
