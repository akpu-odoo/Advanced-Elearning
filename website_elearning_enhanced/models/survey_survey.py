import ast

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    is_eval_survey = fields.Boolean()
