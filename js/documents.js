document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("documentFile");
    const selectButton = document.getElementById("selectDocumentBtn");
    const info = document.getElementById("documentFileInfo");
    const result = document.getElementById("documentResult");

    selectButton.addEventListener("click", () => input.click());

    input.addEventListener("change", async () => {
        const file = input.files[0];
        if (!file) return;

        info.classList.remove("d-none");
        info.innerHTML = `<strong>${escapeHtml(file.name)}</strong> · ${formatFileSize(file.size)}`;

        if (file.size > 10 * 1024 * 1024) {
            showToast("El documento supera el límite de 10 MB.");
            input.value = "";
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append("source_language", document.getElementById("documentSourceLanguage").value);
        formData.append("target_language", document.getElementById("documentTargetLanguage").value);

        result.classList.add("d-none");
        setProcessing("documentProcessing", true);

        try {
            const data = await apiFetch("/api/document", { method: "POST", body: formData });
            document.getElementById("documentOriginal").textContent = data.original;
            document.getElementById("documentTranslation").textContent = data.translation;
            result.classList.remove("d-none");
        } catch (error) {
            showToast(error.message);
        } finally {
            setProcessing("documentProcessing", false);
        }
    });
});
