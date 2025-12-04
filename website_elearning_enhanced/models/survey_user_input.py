from odoo import api, models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    @api.ondelete(at_uninstall=True)
    def _ondelete(self):
        for record in self:
            if record.state == "done":
                record.slide_partner_id.completed = False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.state == "done":
                record.mark_done_on_slide_partner()

        return records

    def write(self, vals):
        super().write(vals)
        if "state" in vals:
            for record in self:
                if record.state == "done":
                    record.mark_done_on_slide_partner()

    def mark_done_on_slide_partner(self):
        for record in self:
            if record.state == "done":
                record.slide_partner_id.completed = True
