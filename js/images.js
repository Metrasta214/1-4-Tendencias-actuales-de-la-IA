document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("imageFile");
    const button = document.getElementById("selectImageBtn");
    const previewWrap = document.getElementById("imagePreviewWrap");
    const preview = document.getElementById("imagePreview");
    const result = document.getElementById("imageResult");

    button.addEventListener("click", () => input.click());

    input.addEventListener("change", async () => {
        const file = input.files[0];
        if (!file) return;

        if (file.size > 10 * 1024 * 1024) {
            showToast("La imagen supera el límite de 10 MB.");
            input.value = "";
            return;
        }

        preview.src = URL.createObjectURL(file);
        previewWrap.classList.remove("d-none");
        result.classList.add("d-none");

        const formData = new FormData();
        formData.append("file", file);
        formData.append("source_language", document.getElementById("imageSourceLanguage").value);
        formData.append("target_language", document.getElementById("imageTargetLanguage").value);

        setProcessing("imageProcessing", true);

        try {
            const data = await apiFetch("/api/image", { method: "POST", body: formData });
            document.getElementById("imageTranslation").textContent = data.translation;
            result.classList.remove("d-none");
        } catch (error) {
            showToast(error.message);
        } finally {
            setProcessing("imageProcessing", false);
        }
    });
});
