from odoo import models


class IrWebsocket(models.AbstractModel):
    _inherit = "ir.websocket"

    def _serve_ir_websocket(self, event_name, data):
        """
        Handle incoming websocket messages.
        Called from websocket.py → WebsocketRequest → serve_websocket_message.
        """
        super()._serve_ir_websocket(event_name, data)

        if event_name == "video_progress":
            self._handle_video_progress(data)

    def _handle_video_progress(self, data):
        slide_id = data.get("slide_id")
        progress = data.get("progress")
        max_progress = data.get("max_progress")

        uid = self.env.uid
        if not uid or not slide_id:
            return

        partner_id = self.env.user.partner_id.id

        partner_slide = (
            self.env["slide.slide.partner"]
            .sudo()
            .search(
                [
                    ("slide_id", "=", slide_id),
                    ("partner_id", "=", partner_id),
                ],
                limit=1,
            )
        )

        if partner_slide and max_progress > partner_slide.max_progress:
            partner_slide.sudo().write(
                {
                    "max_progress": max_progress,
                }
            )

        self.env.cr.commit()
