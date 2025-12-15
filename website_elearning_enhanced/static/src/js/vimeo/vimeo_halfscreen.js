import publicWidget from "@web/legacy/js/public/public_widget";
import { attachVimeoEngine, ensureWebsocket } from "./vimeo_core";

function loadVimeoAPI() {
    return new Promise((resolve) => {
        if (window.Vimeo && window.Vimeo.Player) return resolve();

        const url = "https://player.vimeo.com/api/player.js";
        const script = document.querySelector(`script[src="${url}"]`);

        if (script) {
            const wait = setInterval(() => {
                if (window.Vimeo && window.Vimeo.Player) {
                    clearInterval(wait);
                    resolve();
                }
            }, 150);
            return;
        }

        const s = document.createElement("script");
        s.src = url;
        s.onload = resolve;
        document.head.appendChild(s);
    });
}

function onCompleteSlide() {
    document
        .querySelectorAll(".o_wslides_lesson_aside_list_link")
        .forEach((el) => {
            if (!el.classList.contains("active")) return;

            const sidebar = el.querySelector(".o_wslides_sidebar_done_button");
            if (!sidebar) return;

            if (sidebar.dataset.canSelfMarkCompleted === "True") {
                const btn = el.querySelector(".o_wslides_button_complete");
                if (btn && !btn.disabled) btn.click();
            }
        });
}

publicWidget.registry.VimeoHalfScreenVideoPlayer = publicWidget.Widget.extend({
    selector: ".o_wslides_lesson_content_type iframe[src*='player.vimeo.com']",

    async start() {
        await this._super(...arguments);
        ensureWebsocket();
        await loadVimeoAPI();

        const iframe = this.el;
        const player = new window.Vimeo.Player(iframe);

        const slideId = Number(
            iframe.closest("[data-slide-id]")?.dataset.slideId || 0
        );

        attachVimeoEngine({
            player,
            slideId,
            onComplete: onCompleteSlide,
        });

        return this;
    },
});
