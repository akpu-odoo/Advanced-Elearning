from odoo import fields, models


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    is_eval_survey = fields.Boolean()
