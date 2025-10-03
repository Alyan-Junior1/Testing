from odoo import models, fields, api

class SlackImportWizard(models.TransientModel):
    _name = "slack.import.wizard"
    _description = "Slack Import Wizard"

    folder_path = fields.Char("Slack Export Folder Path", required=True)

    def import_slack_data(self):
        self.env['slack.migration'].migrate_folder(self.folder_path)
        return {'type': 'ir.actions.act_window_close'}
