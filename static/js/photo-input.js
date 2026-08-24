/* Photo drop-zone used by the add/edit place forms.
   Renders one thumbnail + caption input per selected file and keeps the
   FileList in sync so the server can zip photos with their captions. */

(function () {
  const dropZone = document.getElementById("drop-zone");
  const preview = document.getElementById("photo-preview");
  const photoInput =
    document.getElementById("new_photos") || document.getElementById("photos");
  if (!dropZone || !photoInput || !preview) return;

  const MAX_FILES = 5;
  let items = []; // [{ file, caption }]

  function syncInput() {
    const dt = new DataTransfer();
    items.forEach((it) => dt.items.add(it.file));
    photoInput.files = dt.files;
  }

  function render() {
    preview.innerHTML = "";
    items.forEach((it, index) => {
      const card = document.createElement("div");
      card.className = "photo-card";

      const img = document.createElement("img");
      img.src = URL.createObjectURL(it.file);
      img.alt = it.file.name;
      img.addEventListener("load", () => URL.revokeObjectURL(img.src));
      card.appendChild(img);

      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "photo-remove";
      remove.setAttribute("aria-label", "Remove photo");
      remove.innerHTML = "&times;";
      remove.addEventListener("click", () => {
        items.splice(index, 1);
        syncInput();
        render();
      });
      card.appendChild(remove);

      const caption = document.createElement("input");
      caption.type = "text";
      caption.name = "photo_captions";
      caption.maxLength = 140;
      caption.placeholder = "Caption (optional)";
      caption.value = it.caption;
      caption.addEventListener("input", () => {
        it.caption = caption.value;
        // Keep DOM order of caption inputs aligned with the files.
        syncCaptions();
      });
      card.appendChild(caption);

      preview.appendChild(card);
    });
  }

  function syncCaptions() {
    const inputs = preview.querySelectorAll("input[name='photo_captions']");
    items.forEach((it, i) => {
      if (inputs[i]) it.caption = inputs[i].value;
    });
  }

  function handleFiles(fileList) {
    const all = Array.from(fileList).filter((f) => f.type.startsWith("image/"));
    if (!all.length) {
      showToast("No images found", "Choose JPG, PNG or WebP files.", { icon: "alert-circle" });
      return;
    }
    let skipped = false;
    all.forEach((f) => {
      if (items.length >= MAX_FILES) {
        skipped = true;
        return;
      }
      items.push({ file: f, caption: "" });
    });
    if (skipped || all.length < fileList.length) {
      showToast("Some files skipped", `Up to ${MAX_FILES} photos, image files only.`, { icon: "info" });
    }
    syncInput();
    render();
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
