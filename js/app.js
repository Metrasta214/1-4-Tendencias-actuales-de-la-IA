function showToast(message, type = "danger") {
    const container = document.getElementById("toastContainer");
    const wrapper = document.createElement("div");
    const icon = type === "success" ? "check-circle" : type === "warning" ? "exclamation-triangle" : "x-circle";

    wrapper.className = `toast align-items-center text-bg-${type} border-0`;
    wrapper.setAttribute("role", "alert");
    wrapper.innerHTML = `<div class="d-flex"><div class="toast-body"><i class="bi bi-${icon} me-2"></i>${escapeHtml(message)}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>`;

    container.appendChild(wrapper);
    const toast = new bootstrap.Toast(wrapper, { delay: 4500 });
    toast.show();
    wrapper.addEventListener("hidden.bs.toast", () => wrapper.remove());
}

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}

function formatFileSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

async function apiFetch(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, options);
    let data;
    try { data = await response.json(); }
    catch { data = { detail: "El servidor devolvió una respuesta no válida." }; }
    if (!response.ok) throw new Error(data.detail || "La solicitud no pudo completarse.");
    return data;
}

function setProcessing(elementId, visible) {
    const el = document.getElementById(elementId);
    if (el) el.classList.toggle("d-none", !visible);
}

document.addEventListener("DOMContentLoaded", async () => {
    try {
        await apiFetch("/api/health");
        console.log("Backend conectado correctamente.");
    } catch (error) {
        console.warn("Backend no disponible:", error.message);
    }
});
