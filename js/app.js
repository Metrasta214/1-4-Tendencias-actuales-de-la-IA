function showToast(message, type = "danger") {
  const container = document.getElementById("toastContainer");
  if (!container) {
    console.error(message);
    return;
  }

  const wrapper = document.createElement("div");
  const icon =
    type === "success"
      ? "check-circle"
      : type === "warning"
        ? "exclamation-triangle"
        : "x-circle";

  wrapper.className = `toast align-items-center text-bg-${type} border-0`;
  wrapper.setAttribute("role", "alert");

  const content = document.createElement("div");
  content.className = "d-flex";

  const body = document.createElement("div");
  body.className = "toast-body";

  const iconElement = document.createElement("i");
  iconElement.className = `bi bi-${icon} me-2`;

  body.append(iconElement, document.createTextNode(message));

  const closeButton = document.createElement("button");
  closeButton.type = "button";
  closeButton.className = "btn-close btn-close-white me-2 m-auto";
  closeButton.setAttribute("data-bs-dismiss", "toast");

  content.append(body, closeButton);
  wrapper.appendChild(content);
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
  try {
    data = await response.json();
  } catch {
    data = { detail: "El servidor devolvió una respuesta no válida." };
  }

  if (!response.ok) {
    throw new Error(data.detail || "La solicitud no pudo completarse.");
  }

  return data;
}

function setProcessing(elementId, visible) {
  const el = document.getElementById(elementId);
  if (el) el.classList.toggle("d-none", !visible);
}

/* Abrir herramientas desde las tarjetas */
function openFeature(target) {
  const tabButton = document.querySelector(`[data-bs-target="${target}"]`);

  if (tabButton && window.bootstrap?.Tab) {
    bootstrap.Tab.getOrCreateInstance(tabButton).show();
  }

  const panel = document.querySelector(target);
  if (panel) {
    panel.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
    });
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  document.querySelectorAll("[data-feature]").forEach((card) => {
    card.addEventListener("click", () => {
      openFeature(card.dataset.feature);
    });
  });

  /* Verificar conexión con el backend */
  try {
    await apiFetch("/api/health");
    console.log("Backend conectado correctamente.");
  } catch (error) {
    console.warn("Backend no disponible:", error.message);
  }
});
