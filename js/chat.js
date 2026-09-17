
const CHAT_STORAGE_KEY = "linguaAI_conversations";

const chatState = {
    messages: [],
    conversations: [],
    currentConversationId: null,
    isLoading: false
};

// ===============================
// PERSISTENCIA
// ===============================

function loadConversations() {
    try {
        const saved = localStorage.getItem(CHAT_STORAGE_KEY);
        chatState.conversations = saved ? JSON.parse(saved) : [];
    } catch (error) {
        console.error("Error al cargar el historial:", error);
        chatState.conversations = [];
    }
}

function saveConversations() {
    try {
        localStorage.setItem(
            CHAT_STORAGE_KEY,
            JSON.stringify(chatState.conversations)
        );
    } catch (error) {
        showToast("No se pudo guardar el historial.", "warning");
    }
}

function createConversation() {
    const conversation = {
        id: crypto.randomUUID(),
        title: "Nueva conversación",
        messages: [],
        sourceLanguage:
            document.getElementById("chatSourceLanguage").value,
        targetLanguage:
            document.getElementById("chatTargetLanguage").value,
        updatedAt: Date.now()
    };

    chatState.conversations.unshift(conversation);
    chatState.currentConversationId = conversation.id;
    chatState.messages = [];

    saveConversations();
    renderChat();
    renderConversationHistory();

    return conversation;
}

function getCurrentConversation() {
    return chatState.conversations.find(
        conversation =>
            conversation.id === chatState.currentConversationId
    );
}

function saveCurrentConversation() {
    const conversation = getCurrentConversation();

    if (!conversation) return;

    conversation.messages = [...chatState.messages];
    conversation.updatedAt = Date.now();

    if (
        conversation.title === "Nueva conversación" &&
        chatState.messages.length > 0
    ) {
        conversation.title =
            chatState.messages[0].original.slice(0, 35) +
            (chatState.messages[0].original.length > 35 ? "..." : "");
    }

    chatState.conversations.sort(
        (a, b) => b.updatedAt - a.updatedAt
    );

    saveConversations();
    renderConversationHistory();
}

function openConversation(id) {
    const conversation = chatState.conversations.find(
        item => item.id === id
    );

    if (!conversation) return;

    chatState.currentConversationId = id;
    chatState.messages = [...conversation.messages];

    document.getElementById("chatSourceLanguage").value =
        conversation.sourceLanguage;

    document.getElementById("chatTargetLanguage").value =
        conversation.targetLanguage;

    renderChat();
    renderConversationHistory();
}

function deleteConversation(id) {
    chatState.conversations = chatState.conversations.filter(
        conversation => conversation.id !== id
    );

    if (chatState.currentConversationId === id) {
        chatState.currentConversationId = null;
        chatState.messages = [];
    }

    saveConversations();
    renderConversationHistory();
    renderChat();
}

// ===============================
// HISTORIAL LATERAL
// ===============================

function renderConversationHistory() {
    const container = document.getElementById("conversationHistory");

    if (!container) return;

    if (chatState.conversations.length === 0) {
        container.innerHTML = `
            <p class="history-empty">
                Tus conversaciones aparecerán aquí.
            </p>
        `;
        return;
    }

    container.innerHTML = chatState.conversations.map(conversation => `
        <div class="history-item ${
            conversation.id === chatState.currentConversationId
                ? "active"
                : ""
        }">
            <button
                class="history-open"
                data-conversation-id="${conversation.id}"
                title="${escapeHtml(conversation.title)}">
                <i class="bi bi-chat-left-text"></i>
                <span>${escapeHtml(conversation.title)}</span>
            </button>

            <button
                class="history-delete"
                data-delete-id="${conversation.id}"
                aria-label="Eliminar conversación">
                <i class="bi bi-trash3"></i>
            </button>
        </div>
    `).join("");

    container.querySelectorAll("[data-conversation-id]")
        .forEach(button => {
            button.addEventListener("click", () => {
                openConversation(button.dataset.conversationId);
            });
        });

    container.querySelectorAll("[data-delete-id]")
        .forEach(button => {
            button.addEventListener("click", () => {
                deleteConversation(button.dataset.deleteId);
            });
        });
}

// ===============================
// RENDERIZADO DEL CHAT
// ===============================

function scrollChatToBottom(smooth = true) {
    const container = document.getElementById("chatMessages");

    if (!container) return;

    container.scrollTo({
        top: container.scrollHeight,
        behavior: smooth ? "smooth" : "auto"
    });
}

function renderChat() {
    const container = document.getElementById("chatMessages");

    if (!container) return;

    if (chatState.messages.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">
                    <i class="bi bi-translate"></i>
                </div>
                <h3>¿Qué quieres traducir hoy?</h3>
                <p>
                    Escribe un mensaje y recibe su traducción
                    con ayuda de inteligencia artificial.
                </p>
            </div>
        `;
        return;
    }

    container.innerHTML = chatState.messages.map(message => `
        <article class="message user">
            <div class="message-meta">TÚ</div>

            <div class="message-bubble">
                <div class="message-label">Original</div>
                <div class="message-text">
                    ${escapeHtml(message.original)}
                </div>

                <div class="translation-block">
                    <div class="message-label">
                        <i class="bi bi-translate"></i>
                        Traducción
                    </div>

                    <div class="message-text">
                        ${escapeHtml(message.translation)}
                    </div>
                </div>
            </div>
        </article>
    `).join("");

    requestAnimationFrame(() => scrollChatToBottom(false));
}

// ===============================
// ENVÍO DE MENSAJES
// ===============================

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("chatInput");
    const counter = document.getElementById("chatCounter");
    const form = document.getElementById("chatForm");
    const sendBtn = document.getElementById("chatSendBtn");

    if (!input || !form || !sendBtn) return;

    loadConversations();
    renderConversationHistory();

    const latestConversation = chatState.conversations[0];

    if (latestConversation) {
        openConversation(latestConversation.id);
    } else {
        renderChat();
    }

    input.addEventListener("input", () => {
        counter.textContent = `${input.value.length} / 12000`;
    });

    document.getElementById("swapChatLanguages")
        .addEventListener("click", () => {
            const source =
                document.getElementById("chatSourceLanguage");

            const target =
                document.getElementById("chatTargetLanguage");

            [source.value, target.value] =
                [target.value, source.value];

            const conversation = getCurrentConversation();

            if (conversation) {
                conversation.sourceLanguage = source.value;
                conversation.targetLanguage = target.value;
                saveConversations();
            }
        });

    document.getElementById("clearChatBtn")
        .addEventListener("click", () => {
            chatState.messages = [];
            chatState.currentConversationId = null;

            renderChat();
            renderConversationHistory();
        });

    form.addEventListener("submit", async event => {
        event.preventDefault();

        const text = input.value.trim();

        const sourceLanguage =
            document.getElementById("chatSourceLanguage").value;

        const targetLanguage =
            document.getElementById("chatTargetLanguage").value;

        if (!text) {
            return showToast(
                "Escribe un mensaje antes de traducir.",
                "warning"
            );
        }

        if (chatState.isLoading) return;

        if (!chatState.currentConversationId) {
            createConversation();
        }

        chatState.isLoading = true;
        sendBtn.disabled = true;

        sendBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2"></span>
            Procesando
        `;

        try {
            const data = await apiFetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text,
                    source_language: sourceLanguage,
                    target_language: targetLanguage,
                    history: chatState.messages.slice(-8)
                })
            });

            chatState.messages.push({
                original: data.original,
                translation: data.translation
            });

            saveCurrentConversation();
            renderChat();

            input.value = "";
            counter.textContent = "0 / 12000";

        } catch (error) {
            showToast(error.message);

        } finally {
            chatState.isLoading = false;
            sendBtn.disabled = false;

            sendBtn.innerHTML = `
                <i class="bi bi-send"></i>
                Traducir
            `;
        }
    });

    // Crear una conversación nueva desde el botón lateral.
    const newChatBtn = document.getElementById("newChatBtn");

    if (newChatBtn) {
        newChatBtn.addEventListener("click", () => {
            chatState.currentConversationId = null;
            chatState.messages = [];

            renderChat();
            renderConversationHistory();
            input.focus();
        });
    }
});