import { user } from "@web/core/user";
import { session } from "@web/session";

let ws = null;
let wsReady = false;

export function ensureWebsocket() {
    if (
        ws &&
        (ws.readyState === WebSocket.OPEN ||
            ws.readyState === WebSocket.CONNECTING)
    ) {
        return;
    }

    const loc = window.location;
    const protocol = loc.protocol === "https:" ? "wss:" : "ws:";
    const url = `${protocol}//${loc.host}/websocket?version=${
        session.websocket_worker_version || "saas-18.5-1"
    }`;

    ws = new WebSocket(url);
    wsReady = false;

    ws.onopen = () => {
        wsReady = true;
    };

    ws.onclose = () => (wsReady = false);
    ws.onerror = () => (wsReady = false);
}

export function sendVideoProgress(
    slideId,
    progress,
    maxProgress,
    isFinal = false
) {
    if (!wsReady) return;
    ws.send(
        JSON.stringify({
            event_name: "video_progress",
            data: {
                slide_id: slideId,
                progress,
                max_progress: maxProgress,
                final: isFinal,
            },
        })
    );
}

const pKey = (sid) => `vimeo_p_s${sid}_u${user.userId}`;
const mKey = (sid) => `vimeo_m_s${sid}_u${user.userId}`;

export const loadProgress = (sid) => parseFloat(localStorage.getItem(pKey(sid)) || 0);
export const saveProgress = (sid, val) => localStorage.setItem(pKey(sid), val);

export const loadMax = (sid) => parseFloat(localStorage.getItem(mKey(sid)) || 0);
export const saveMax = (sid, val) => localStorage.setItem(mKey(sid), val);

export async function attachVimeoEngine({
    player,
    slideId,
    onComplete = null,
}) {
    ensureWebsocket();

    let lastAllowed = loadProgress(slideId);
    let maxProgress = loadMax(slideId);
    let lastSendTs = 0;
    let duration = await player.getDuration();

    player.setPlaybackRate(1).catch(() => {});
    player.on("playbackratechange", () => player.setPlaybackRate(1));

    if (lastAllowed > 1) {
        player.setCurrentTime(lastAllowed).catch(() => {});
    }

    player.on("timeupdate", ({ seconds }) => {
        const t = seconds;

        saveProgress(slideId, t);
        if (t > maxProgress) {
            maxProgress = t;
            saveMax(slideId, t);
        }

        if (t > lastAllowed + 0.8) {
            player.setCurrentTime(lastAllowed).catch(() => {});
            return;
        }
        lastAllowed = Math.max(lastAllowed, t);

        const now = Date.now();
        if (now - lastSendTs >= 10000) {
            lastSendTs = now;
            if (t >= maxProgress)
                sendVideoProgress(slideId, t, maxProgress, false);
        }
    });

    player.on("seeked", async () => {
        const t = await player.getCurrentTime();
        if (t > lastAllowed + 0.8) {
            player.setCurrentTime(lastAllowed).catch(() => {});
        }
    });

    player.on("ended", () => {
        saveProgress(slideId, duration);
        saveMax(slideId, duration);
        sendVideoProgress(slideId, duration, duration, true);

        if (onComplete) onComplete();
    });
}
