import { renderToElement } from "@web/core/utils/render";
import Fullscreen from "@website_slides/js/slides_course_fullscreen_player";

const superOnChangeSlideRequest = Fullscreen.prototype._onChangeSlideRequest;

Fullscreen.include({
    _onChangeSlideRequest: async function (ev) {
        const res = await this.bindService("orm").call(
            "slide.slide",
            "is_slide_accessible",
            [ev.data.id]
        );
        if (!res["is_completed"]) {
            this.bindService("notification").add(
                "Please Watch all the lessons before accessing this one",
                {
                    type: "danger",
                    title: "Access Denied",
                }
            );
            ev.stopPropagation();
            return;
        }
        superOnChangeSlideRequest.call(this, ev);
    },

    _renderSlide: function () {
        if (this._slideValue.category == "eval_survey") {
            const def = this._super.apply(this, arguments);
            const contentEl = this.el.querySelector(".o_wslides_fs_content");
            if (this._slideValue.category === "eval_survey") {
                contentEl.textContent = "";
                contentEl.append(
                    renderToElement("website.slides.fullscreen.eval_survey", {
                        widget: this,
                    })
                );
            }
            return Promise.all([def]);
        }
        return this._super.apply(this, arguments);
    },
});
