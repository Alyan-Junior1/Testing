{
    'name': 'Slack Data Migration',
    'version': '1.0',
    'category': 'Discuss',
    'summary': 'Migrate Slack messages, files, and images to Odoo Discuss',
    'description': 'Import Slack export including channels, messages, files, and images into Odoo Discuss app.',
    'author': 'Alyan Junior',
    'depends': ['base', 'mail', 'discuss'],
    'data': [
        'wizards/slack_import_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}
