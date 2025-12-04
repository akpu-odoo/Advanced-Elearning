from odoo.http import request
from odoo.addons.website_slides.controllers.main import WebsiteSlides


class WebsiteSlidesEnhanced(WebsiteSlides):

    def slide_view(self, slide, **kwargs):
        if slide and not slide.sudo().is_slide_accessible(slide).get("is_completed"):
            return request.render(
                "website_elearning_enhanced.slide_access_popup",
                {
                    "show_popup": True,
                    "channel": slide.channel_id,
                },
            )
        return super().slide_view(slide, **kwargs)

    def _prepare_additional_channel_values(self, values, **kwargs):
        res = super()._prepare_additional_channel_values(values, **kwargs)
        channel = values.get("channel")

        eval_survey_data = []

        if not channel:
            res["eval_survey_data"] = eval_survey_data
            return res

        survey_slides = channel.slide_ids.filtered(
            lambda s: s.slide_category == "eval_survey" and s.survey_id
        )

        if not survey_slides:
            res["eval_survey_data"] = eval_survey_data
            return res

        surveys = survey_slides.mapped("survey_id")

        all_questions = surveys.mapped("question_ids").filtered(
            lambda q: q.question_type in ("numerical_box", "scale")
        )

        if not all_questions:
            res["eval_survey_data"] = eval_survey_data
            return res

        completed_inputs = surveys.mapped("user_input_ids").filtered(
            lambda u: u.state == "done"
        )

        if not completed_inputs:
            res["eval_survey_data"] = eval_survey_data
            return res

        all_lines = completed_inputs.mapped("user_input_line_ids")

        lines_by_question = {}
        for line in all_lines:
            qid = line.question_id.id
            lines_by_question.setdefault(qid, []).append(line)

        for q in all_questions:
            q_lines = lines_by_question.get(q.id, [])
            if not q_lines:
                continue

            if q.question_type == "numerical_box":
                values = [
                    line.value_numerical_box
                    for line in q_lines
                    if line.value_numerical_box is not None
                ]
            else:
                values = [
                    line.value_scale for line in q_lines if line.value_scale is not None
                ]

            if not values:
                continue

            avg_value = sum(values) / len(values)

            eval_survey_data.append(
                {
                    "question": q.title,
                    "average": round(avg_value, 2),
                    "type": q.question_type,
                    "participants": len(values),
                }
            )

        res["eval_survey_data"] = eval_survey_data
        return res
