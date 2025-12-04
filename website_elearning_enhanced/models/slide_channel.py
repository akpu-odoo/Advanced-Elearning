from odoo import fields, models


class SlideChannel(models.Model):
    _inherit = "slide.channel"

    sequential_slides = fields.Boolean(
        string="Sequential locking for slides", default=False
    )
    nbr_eval_survey = fields.Integer(
        "Number of Certifications", compute="_compute_slides_statistics", store=True
    )
