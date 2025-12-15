from odoo import fields, models


class SlideSlidePartner(models.Model):
    _inherit = "slide.slide.partner"

    status = fields.Selection(
        [
            ("new", "New"),
            ("in_progress", "In Progress"),
            ("done", "Completed"),
        ],
        default="in_progress",
    )
    max_progress = fields.Integer(string="Max Progress", default=0)
    completion_timestamp = fields.Datetime(string="Completion Timestamp")

    def write(self, vals):
        if vals.get("completed"):
            vals["completion_timestamp"] = fields.Datetime.now()
            vals["status"] = "done"
        return super().write(vals)
