document.addEventListener("DOMContentLoaded", () => {
  const startButton = document.getElementById("startRecordingBtn");
  const stopButton = document.getElementById("stopRecordingBtn");
  const status = document.getElementById("audioStatus");
  const indicator = document.getElementById("recordingIndicator");
  const info = document.getElementById("audioFileInfo");
  const result = document.getElementById("audioResult");

  if (!startButton || !stopButton) return;

  let mediaRecorder = null;
  let stream = null;
  let chunks = [];

  startButton.addEventListener("click", startRecording);
  stopButton.addEventListener("click", stopRecording);

  async function startRecording() {
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      showToast(
        "Tu navegador no permite grabar audio. Prueba con Chrome o Edge y usa HTTPS.",
        "warning",
      );
      return;
    }

    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";

      mediaRecorder = new MediaRecorder(stream, { mimeType });
      chunks = [];

      mediaRecorder.addEventListener("dataavailable", (event) => {
        if (event.data && event.data.size > 0) {
          chunks.push(event.data);
        }
      });

      mediaRecorder.addEventListener("stop", processRecording, { once: true });

      mediaRecorder.start();

      startButton.disabled = true;
      stopButton.disabled = false;
      indicator.classList.remove("d-none");
      status.textContent = "Te estamos escuchando. Habla con claridad.";
      info.classList.add("d-none");
      result.classList.add("d-none");
    } catch (error) {
      showToast(
        error.name === "NotAllowedError"
          ? "Debes permitir el acceso al micrófono."
          : "No se pudo iniciar el micrófono.",
      );
    }
  }

  function stopRecording() {
    if (!mediaRecorder || mediaRecorder.state === "inactive") return;

    mediaRecorder.stop();
    stopButton.disabled = true;
    indicator.classList.add("d-none");
    status.textContent = "Procesando tu voz...";
  }

  async function processRecording() {
    try {
      const mimeType = mediaRecorder.mimeType || "audio/webm";
      const audioBlob = new Blob(chunks, { type: mimeType });

      if (audioBlob.size === 0) {
        throw new Error("No se detectó audio. Intenta hablar de nuevo.");
      }

      if (audioBlob.size > 10 * 1024 * 1024) {
        throw new Error("La grabación supera el límite de 10 MB.");
      }

      const extension = mimeType.includes("ogg") ? "ogg" : "webm";
      const audioFile = new File([audioBlob], `grabacion.${extension}`, {
        type: mimeType,
      });

      info.textContent = `Grabación lista · ${formatFileSize(audioBlob.size)}`;
      info.classList.remove("d-none");

      const formData = new FormData();
      formData.append("file", audioFile);
      formData.append(
        "source_language",
        document.getElementById("audioSourceLanguage").value,
      );
      formData.append(
        "target_language",
        document.getElementById("audioTargetLanguage").value,
      );

      setProcessing("audioProcessing", true);
      result.classList.add("d-none");

      const data = await apiFetch("/api/audio", {
        method: "POST",
        body: formData,
      });

      document.getElementById("audioTranscript").textContent =
        data.transcript ?? "";

      document.getElementById("audioTranslation").textContent =
        data.translation ?? "";

      document.getElementById("audioPlayer").src =
        `data:${data.audio_mime};base64,${data.audio_base64}`;

      result.classList.remove("d-none");
      status.textContent = "Traducción completada.";
    } catch (error) {
      showToast(error.message);
      status.textContent = "No se pudo procesar la grabación.";
    } finally {
      setProcessing("audioProcessing", false);
      startButton.disabled = false;
      stopButton.disabled = true;

      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
        stream = null;
      }
    }
  }
});
