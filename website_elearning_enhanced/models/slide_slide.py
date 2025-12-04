from odoo import api, fields, models


class SlideSlide(models.Model):
    _inherit = "slide.slide"

    slide_category = fields.Selection(
        selection_add=[("eval_survey", "Evaluation Survey")],
        ondelete={"eval_survey": "set default"},
    )
    nbr_eval_survey = fields.Integer(
        "Number of Survey", compute="_compute_slides_statistics", store=True, default=1
    )
    slide_type = fields.Selection(
        selection_add=[("eval_survey", "Evaluation Survey")],
        ondelete={"eval_survey": "set null"},
    )

    @api.model
    def is_slide_accessible(self, slide):
        if type(slide) == int:
            slide = self.env["slide.slide"].browse(slide)

        if not slide.channel_id.sequential_slides:
            return {
                "is_completed": True,
                "is_category": slide.slide_category,
            }

        for slide_id in slide.channel_id.slide_ids:
            if slide_id.is_category:
                continue
            if slide_id.sequence >= slide.sequence:
                return {
                    "is_completed": True,
                    "is_category": slide.slide_category,
                }

            is_completed = False
            for partner in slide_id.sudo().slide_partner_ids:
                if (
                    partner.partner_id.id == self.env.user.partner_id.id
                    and partner.completed
                ):
                    is_completed = True
                    break
            if not is_completed:
                return {
                    "is_completed": False,
                    "is_category": slide.slide_category,
                }

        return {
            "is_completed": True,
            "is_category": slide.slide_category,
        }

    def _generate_certification_url(self):
        certification_urls = super()._generate_certification_url()
        for slide in self.filtered(
            lambda slide: slide.slide_category == "eval_survey" and slide.survey_id
        ):
            if slide.channel_id.is_member:
                user_membership_id_sudo = slide.user_membership_id.sudo()
                if user_membership_id_sudo.user_input_ids:
                    last_user_input = next(
                        user_input
                        for user_input in user_membership_id_sudo.user_input_ids.sorted(
                            lambda user_input: user_input.create_date, reverse=True
                        )
                    )
                    certification_urls[slide.id] = last_user_input.get_start_url()
                else:
                    user_input = slide.survey_id.sudo()._create_answer(
                        partner=self.env.user.partner_id,
                        check_attempts=False,
                        **{
                            "slide_id": slide.id,
                            "slide_partner_id": user_membership_id_sudo.id,
                        },
                        invite_token=self.env[
                            "survey.user_input"
                        ]._generate_invite_token()
                    )
                    certification_urls[slide.id] = user_input.get_start_url()
            else:
                user_input = slide.survey_id.sudo()._create_answer(
                    partner=self.env.user.partner_id,
                    check_attempts=False,
                    test_entry=True,
                    **{"slide_id": slide.id}
                )
                certification_urls[slide.id] = user_input.get_start_url()
        return certification_urls

    @api.model_create_multi
    def create(self, vals_list):
        slides = super().create(vals_list)
        slides_with_survey = slides.filtered("survey_id")
        for slide in slides_with_survey:
            if slide.survey_id.is_eval_survey:
                slide.slide_category = "eval_survey"
                slide.slide_type = "eval_survey"
        return slides
