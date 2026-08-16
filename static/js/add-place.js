/* Add place form — photo drag/drop + preview. Submission is a real POST. */

(function () {
  const dropZone = document.getElementById("drop-zone");
  const photoInput = document.getElementById("photos");
  const preview = document.getElementById("photo-preview");
  if (!dropZone || !photoInput || !preview) return;

  const MAX_FILES = 5;

  function handleFiles(files) {
    const list = Array.from(files).filter((f) => f.type.startsWith("image/")).slice(0, MAX_FILES);
    if (!list.length) {
      showToast("No images found", "Choose JPG, PNG or WebP files.", { icon: "alert-circle" });
      return;
    }
    if (list.length < Array.from(files).length) {
      showToast("Some files skipped", "Up to 5 photos, image files only.", { icon: "info" });
    }

    const dt = new DataTransfer();
    list.forEach((f) => dt.items.add(f));
    photoInput.files = dt.files;

    preview.innerHTML = "";
    list.forEach((file) => {
      const img = document.createElement("img");
      img.src = URL.createObjectURL(file);
      img.alt = file.name;
      img.addEventListener("load", () => URL.revokeObjectURL(img.src));
      preview.appendChild(img);
    });
  }

  dropZone.addEventListener("click", () => photoInput.click());
  photoInput.addEventListener("change", (e) => {
    if (e.target.files.length) handleFiles(e.target.files);
  });

  ["dragenter", "dragover"].forEach((evt) =>
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropZone.classList.add("dragging");
    })
  );
  ["dragleave", "drop"].forEach((evt) =>
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropZone.classList.remove("dragging");
    })
  );
  dropZone.addEventListener("drop", (e) => {
    if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files);
  });
})();
