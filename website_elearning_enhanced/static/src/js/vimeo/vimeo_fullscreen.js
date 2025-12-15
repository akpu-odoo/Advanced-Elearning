import publicWidget from "@web/legacy/js/public/public_widget";
import Fullscreen from "@website_slides/js/slides_course_fullscreen_player";
import { attachVimeoEngine, ensureWebsocket } from "./vimeo_core";

function loadVimeoAPI() {
    return new Promise((resolve) => {
        if (window.Vimeo && window.Vimeo.Player) return resolve();

        const url = "https://player.vimeo.com/api/player.js";
        const script = document.querySelector(`script[src="${url}"]`);

        if (!script) {
            const s = document.createElement("script");
            s.src = url;
            s.onload = resolve;
            document.head.appendChild(s);
        } else {
            const wait = setInterval(() => {
                if (window.Vimeo && window.Vimeo.Player) {
                    clearInterval(wait);
                    resolve();
                }
            }, 150);
        }
    });
}

const VimeoVideoPlayer = publicWidget.Widget.extend({
    template: "website.slides.fullscreen.video.vimeo",

    init(parent, slide) {
        this._super(...arguments);
        this.parent = parent;
        this.slide = slide;
        this.player = null;
    },

    willStart() {
        return Promise.all([this._super(...arguments), loadVimeoAPI()]);
    },

    async start() {
        await this._super(...arguments);
        await this._attachPlayer();
    },

    async _attachPlayer() {
        ensureWebsocket();

        const iframe = this.el.querySelector("iframe");
        this.player = new window.Vimeo.Player(iframe);

        attachVimeoEngine({
            player: this.player,
            slideId: this.slide.id,
            onComplete: () => {
                if (
                    this.slide.isMember &&
                    !this.slide.hasQuestion &&
                    !this.slide.completed
                ) {
                    this.trigger_up("slide_mark_completed", this.slide);
                }
                if (this.slide.hasNext) {
                    setTimeout(() => {
                        this.trigger_up("slide_go_next", this.slide);
                    }, 2000);
                }
            },
        });
    },
});

Fullscreen.include({
    async _renderSlide() {
        const res = await this._super(...arguments);

        const slide = this._slideValue;
        if (!slide) return res;

        if (slide.category === "video" && slide.videoSourceType === "vimeo") {
            const container = this.$(".o_wslides_fs_content");
            container.empty();

            const player = new VimeoVideoPlayer(this, slide);
            await player.appendTo(container);
        }

        return res;
    },
});

export default Fullscreen;
