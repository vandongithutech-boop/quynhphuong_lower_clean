function enableProductionVoice() {
    localStorage.setItem("production_voice_enabled", "1");

    speakVietnamese("Đã bật thông báo giọng đọc tiếng Việt cho bộ phận sản xuất.");
}

function getVietnameseVoice() {
    const voices = window.speechSynthesis.getVoices();

    return voices.find(v => v.lang === "vi-VN")
        || voices.find(v => v.lang && v.lang.startsWith("vi"))
        || voices.find(v => v.name.toLowerCase().includes("vietnam"))
        || null;
}

function speakVietnamese(text) {
    if (!("speechSynthesis" in window)) return;

    window.speechSynthesis.cancel();

    const msg = new SpeechSynthesisUtterance(text);
    msg.lang = "vi-VN";
    msg.rate = 0.85;
    msg.pitch = 1;

    const viVoice = getVietnameseVoice();

    if (viVoice) {
        msg.voice = viVoice;
    }

    window.speechSynthesis.speak(msg);
}

function checkNewProductionOrders() {
    const enabled = localStorage.getItem("production_voice_enabled") === "1";
    if (!enabled) return;

    fetch(PRODUCTION_VOICE_API)
        .then(response => response.json())
        .then(data => {
            for (const order of data.orders) {
                const key = "spoken_order_" + order.order_code;

                if (!localStorage.getItem(key)) {
                    localStorage.setItem(key, "1");
                    sessionStorage.setItem("voice_after_reload", order.voice_text);

                    window.location.reload();
                    break;
                }
            }
        })
        .catch(error => console.log("Voice check error:", error));
}

document.addEventListener("DOMContentLoaded", function () {
    const textAfterReload = sessionStorage.getItem("voice_after_reload");

    if (textAfterReload) {
        sessionStorage.removeItem("voice_after_reload");

        setTimeout(function () {
            speakVietnamese(textAfterReload);
        }, 800);
    }

    setInterval(checkNewProductionOrders, 10000);
});

window.speechSynthesis.onvoiceschanged = function () {
    window.speechSynthesis.getVoices();
};
