const chatState = { messages: [] };

function renderChat() {
    const container = document.getElementById("chatMessages");
    if (chatState.messages.length === 0) {
        container.innerHTML = `<div class="empty-state"><i class="bi bi-translate"></i><h3>Inicia la conversación</h3><p>Escribe un mensaje y recibe su traducción con contexto.</p></div>`;
        return;
    }

    container.innerHTML = chatState.messages.map(message => `
        <article class="message user">
            <div class="message-meta">TÚ</div>
            <div class="message-bubble">
                <div class="message-label">Original</div>
                <div class="message-text">${escapeHtml(message.original)}</div>
                <div class="translation-block">
                    <div class="message-label">Traducción</div>
                    <div class="message-text">${escapeHtml(message.translation)}</div>
                </div>
            </div>
        </article>
    `).join("");

    container.scrollTop = container.scrollHeight;
}

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("chatInput");
    const counter = document.getElementById("chatCounter");
    const form = document.getElementById("chatForm");
    const sendBtn = document.getElementById("chatSendBtn");

    input.addEventListener("input", () => counter.textContent = `${input.value.length} / 12000`);

    document.getElementById("swapChatLanguages").addEventListener("click", () => {
        const source = document.getElementById("chatSourceLanguage");
        const target = document.getElementById("chatTargetLanguage");
        [source.value, target.value] = [target.value, source.value];
    });

    document.getElementById("clearChatBtn").addEventListener("click", () => {
        chatState.messages = [];
        renderChat();
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const text = input.value.trim();
        const sourceLanguage = document.getElementById("chatSourceLanguage").value;
        const targetLanguage = document.getElementById("chatTargetLanguage").value;

        if (!text) return showToast("Escribe un mensaje antes de traducir.", "warning");

        sendBtn.disabled = true;
        sendBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando';

        try {
            const data = await apiFetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text,
                    source_language: sourceLanguage,
                    target_language: targetLanguage,
                    history: chatState.messages.slice(-8)
                })
            });

            chatState.messages.push({ original: data.original, translation: data.translation });
            renderChat();
            input.value = "";
            counter.textContent = "0 / 12000";
        } catch (error) {
            showToast(error.message);
        } finally {
            sendBtn.disabled = false;
            sendBtn.innerHTML = '<i class="bi bi-send"></i> Traducir';
        }
    });
});
