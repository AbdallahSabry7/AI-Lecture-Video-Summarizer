const toast = document.getElementById("toast");
const apiInput = document.getElementById("apiBase");
const textInput = document.getElementById("textInput");
const textSummary = document.getElementById("textSummary");
const textButton = document.getElementById("textSubmit");
const mediaInput = document.getElementById("mediaInput");
const mediaButton = document.getElementById("mediaSubmit");
const mediaTranscript = document.getElementById("mediaTranscript");
const mediaSummary = document.getElementById("mediaSummary");

const loadApiBase = () => {
  const saved = localStorage.getItem("summarizer:apiBase");
  if (saved) return saved;
  // Default to relative path if served from same origin, otherwise use input value
  return apiInput.value || "/api";
};
const saveApiBase = (value) => localStorage.setItem("summarizer:apiBase", value);

apiInput.value = loadApiBase();
apiInput.addEventListener("change", (event) => {
  saveApiBase(event.target.value.trim());
});

const showToast = (message, timeout = 3500) => {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast.timeoutId);
  showToast.timeoutId = setTimeout(() => toast.classList.remove("show"), timeout);
};

const summarizeText = async () => {
  const text = textInput.value.trim();
  if (!text) {
    showToast("Please paste some text first.");
    return;
  }

  textButton.disabled = true;
  textButton.textContent = "Summarizing...";
  try {
    const response = await fetch(`${loadApiBase()}/summarize-text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!response.ok) {
      let errorMsg = "Failed to summarize text";
      try {
        const errorData = await response.json();
        if (errorData?.detail) {
          errorMsg = errorData.detail;
        }
      } catch {
        // Ignore JSON parse errors
      }
      throw new Error(errorMsg);
    }
    const data = await response.json();
    textSummary.value = data.summary || "No important content detected.";
    textSummary.classList.remove("placeholder");
    showToast("Text summarized successfully!");
  } catch (error) {
    console.error(error);
    showToast(`Error: ${error.message || "Something went wrong."}`);
    textSummary.value = "";
    textSummary.classList.add("placeholder");
  } finally {
    textButton.disabled = false;
    textButton.textContent = "Summarize";
  }
};

const processMedia = async () => {
  const file = mediaInput.files?.[0];
  if (!file) {
    showToast("Select an audio or video file first.");
    return;
  }

  mediaButton.disabled = true;
  mediaButton.textContent = "Processing...";
  mediaTranscript.value = "";
  mediaSummary.value = "";

  try {
    const formData = new FormData();
    formData.append("file", file);
    
    // Create AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minute timeout
    
    const response = await fetch(`${loadApiBase()}/transcribe-and-summarize`, {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    if (!response.ok) {
      let errorMsg = "Failed to process media file";
      try {
        const errorData = await response.json();
        if (errorData?.detail) {
          errorMsg = errorData.detail;
        }
      } catch {
        // Ignore JSON parse errors
      }
      throw { message: errorMsg, response };
    }
    const data = await response.json();
    mediaTranscript.value = data.transcript || "";
    mediaSummary.value = data.summary || "";
    if (!data.transcript) {
      showToast("Warning: No transcript generated. Check if ffmpeg is installed.");
    } else {
      showToast("Media processed successfully!");
    }
  } catch (error) {
    console.error(error);
    let errorMsg = "Something went wrong.";
    if (error.name === "AbortError") {
      errorMsg = "Request timed out. The file may be too large or processing is taking too long.";
    } else if (error.message) {
      errorMsg = error.message;
    }
    showToast(`Error: ${errorMsg}`);
    mediaTranscript.value = "";
    mediaSummary.value = "";
  } finally {
    mediaButton.disabled = false;
    mediaButton.textContent = "Upload & Process";
  }
};

textButton.addEventListener("click", summarizeText);
mediaButton.addEventListener("click", processMedia);

