document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("audioFile");
    const selectButton = document.getElementById("selectAudioBtn");
    const info = document.getElementById("audioFileInfo");
    const result = document.getElementById("audioResult");

    selectButton.addEventListener("click", () => input.click());

    input.addEventListener("change", async () => {
        const file = input.files[0];
        if (!file) return;

        info.classList.remove("d-none");
        info.innerHTML = `<strong>${escapeHtml(file.name)}</strong> · ${formatFileSize(file.size)}`;

        if (file.size > 10 * 1024 * 1024) {
            showToast("El audio supera el límite de 10 MB.");
            input.value = "";
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append("source_language", document.getElementById("audioSourceLanguage").value);
        formData.append("target_language", document.getElementById("audioTargetLanguage").value);

        result.classList.add("d-none");
        setProcessing("audioProcessing", true);

        try {
            const data = await apiFetch("/api/audio", { method: "POST", body: formData });
            document.getElementById("audioTranscript").textContent = data.transcript;
            document.getElementById("audioTranslation").textContent = data.translation;
            document.getElementById("audioPlayer").src = `data:${data.audio_mime};base64,${data.audio_base64}`;
            result.classList.remove("d-none");
        } catch (error) {
            showToast(error.message);
        } finally {
            setProcessing("audioProcessing", false);
        }
    });
});
