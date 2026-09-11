const dropzone = document.getElementById("dropzone");
const dropzoneText = document.getElementById("dropzone-text");
const fileInput = document.getElementById("file-input");
const toast = document.getElementById("toast");

// --- Show the chosen filename ---
fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    dropzoneText.textContent = fileInput.files[0].name;
  }
});

// --- Drag and drop onto the dropzone ---
["dragover", "dragleave", "drop"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (e) => e.preventDefault());
});

dropzone.addEventListener("dragover", () => dropzone.classList.add("is-dragover"));
dropzone.addEventListener("dragleave", () => dropzone.classList.remove("is-dragover"));

dropzone.addEventListener("drop", (e) => {
  dropzone.classList.remove("is-dragover");
  const dropped = e.dataTransfer.files;
  if (dropped.length > 0) {
    fileInput.files = dropped;
    dropzoneText.textContent = dropped[0].name;
  }
});

// --- Click a swatch to copy its hex code ---
document.querySelectorAll(".swatch").forEach((swatch) => {
  swatch.addEventListener("click", async () => {
    const hex = swatch.dataset.hex;
    try {
      await navigator.clipboard.writeText(hex);
      showToast(`Copied ${hex}`);
    } catch (err) {
      showToast("Couldn't copy — try selecting the text manually.");
    }
  });
});

let toastTimeout = null;
function showToast(message) {
  toast.textContent = message;
  toast.classList.add("is-visible");
  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => toast.classList.remove("is-visible"), 1600);
}
