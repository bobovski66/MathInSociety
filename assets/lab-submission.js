/* Create a readable, filled-in HTML copy of a Math in Society lab.
   The file shows the student's responses and does not need this browser's storage. */
(function () {
  "use strict";

  const presentationStyle = [
    "body{background:#f7f7f3;color:#223028;font-family:system-ui,-apple-system,Segoe UI,sans-serif;line-height:1.55}",
    ".submission-cover{background:#fff;border:1px solid #cbd6cd;border-radius:12px;padding:20px 24px;margin:0 0 24px}",
    ".submission-cover h2{font-size:1.25rem;margin:0 0 7px;color:#294532}",
    ".submission-cover p{margin:4px 0}",
    ".submission-answer{display:block;min-height:2em;max-width:100%;background:#fff;border:1px solid #b7c9bc;",
    " border-radius:7px;margin:7px 0 15px;padding:9px 12px;color:#172c21;white-space:pre-wrap;overflow-wrap:anywhere;font-weight:600}",
    ".submission-answer.unanswered{font-weight:400;font-style:italic;color:#67766b}",
    ".submission-copy .question{break-inside:avoid}",
    ".submission-copy .question label{display:block;font-weight:600}",
    ".submission-copy .lab-part{break-inside:auto}",
    ".submission-copy .hero{margin-bottom:20px}",
    ".submission-copy .print-answer{display:none!important}",
    ".submission-copy img{max-width:100%;height:auto}",
    ".submission-copy mjx-container{max-width:100%}",
    "@media print{body{background:#fff!important}.submission-cover{border:0;border-bottom:1px solid #aaa;",
    "border-radius:0;padding:0 0 12px}.submission-answer{border-color:#aaa;background:#fff!important}}"
  ].join("");

  function safeName(value) {
    return String(value).normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
      .trim().replace(/[^a-zA-Z0-9_-]+/g, "_").replace(/^_+|_+$/g, "").slice(0,65) || "Student";
  }

  function escapeHTML(value) {
    return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function responseText(field) {
    if (field.tagName === "SELECT") {
      if (!field.value) return "";
      const selected = Array.from(field.options || []).find(function (opt) { return opt.value === field.value; });
      return selected ? selected.textContent.trim() : String(field.value);
    }
    if (field.type === "checkbox") return field.checked ? "Checked" : "Not checked";
    if (field.type === "radio") return field.checked ? "Selected" : "Not selected";
    return String(field.value || "");
  }

  function freezeResponses(original, copy) {
    const sourceFields = Array.from(original.querySelectorAll("input,select,textarea"));
    const savedFields = Array.from(copy.querySelectorAll("input,select,textarea"));
    savedFields.forEach(function (field, index) {
      const source = sourceFields[index];
      if (!source) { field.remove(); return; }
      const result = document.createElement("div");
      result.className = "submission-answer";
      const answer = responseText(source).trim();
      result.textContent = answer || "Not answered";
      if (!answer) result.classList.add("unanswered");
      field.replaceWith(result);
    });
  }

  async function embedPictures(copy) {
    const pictures = Array.from(copy.querySelectorAll("img[src]"));
    await Promise.all(pictures.map(async function (img) {
      const old = img.getAttribute("src");
      try {
        const absolute = new URL(old, document.baseURI);
        img.src = absolute.href;
        if (absolute.origin !== window.location.origin) return;
        const response = await fetch(absolute.href, {cache:"force-cache"});
        if (!response.ok) return;
        const blob = await response.blob();
        if (blob.type.includes("svg") || /\.svg$/i.test(absolute.pathname)) {
          const svg = await blob.text();
          img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
        } else if (typeof FileReader !== "undefined") {
          img.src = await new Promise(function (resolve, reject) {
            const reader = new FileReader();
            reader.onload = function () { resolve(reader.result); };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
          });
        }
      } catch (error) {
        // Keep the original absolute link if embedding this illustration fails.
        try { img.src = new URL(old, document.baseURI).href; } catch (_) {}
      }
    }));
  }

  async function pageStyles() {
    const pieces = [];
    const entries = Array.from(document.head.querySelectorAll("style,link[rel='stylesheet']"));
    for (const el of entries) {
      if (el.tagName === "STYLE") {
        pieces.push(el.textContent);
        continue;
      }
      try {
        const response = await fetch(el.href, {cache:"force-cache"});
        if (!response.ok) throw new Error("Could not load stylesheet");
        const base = el.href;
        let css = await response.text();
        css = css.replace(/url\(\s*(['"]?)([^'")]+)\1\s*\)/g, function (match, quote, url) {
          if (/^(?:data:|#)/i.test(url)) return match;
          try { return 'url("' + new URL(url, base).href + '")'; } catch (_) { return match; }
        });
        pieces.push(css);
      } catch (error) {
        // Normal course styles can still load over the internet if needed.
        pieces.push('@import url("' + el.href.replace(/"/g, "%22") + '");');
      }
    }
    return pieces.join("\n");
  }

  function cleanSubmission(copy) {
    copy.classList.add("submission-copy");
    copy.removeAttribute("data-answer-store");
    copy.removeAttribute("data-legacy-store");
    // Remove checking UI and answer keys, but keep all question wording and figures.
    copy.querySelectorAll(".student-bar,.progress,.no-print,.actions,.next,.footer,.print-name," +
      ".print-answer,.field-feedback,.section-feedback,button,script").forEach(function (node) { node.remove(); });
    copy.querySelectorAll("[hidden]").forEach(function (node) { node.remove(); });
    copy.querySelectorAll("[data-answer],[data-hint],[data-tolerance],[data-success]").forEach(function (node) {
      ["data-answer","data-hint","data-tolerance","data-success"].forEach(function (attr) { node.removeAttribute(attr); });
    });
    copy.querySelectorAll("a[href]").forEach(function (link) {
      try { link.href = new URL(link.getAttribute("href"), document.baseURI).href; } catch (_) {}
    });
  }

  async function downloadFilledLab(button) {
    const main = document.querySelector("main[data-answer-store]");
    const nameControl = document.getElementById("studentName");
    const status = document.getElementById("printStatus");
    if (!main || !nameControl) return;
    const student = nameControl.value.trim();
    if (!student) {
      if (status) status.textContent = "Enter your name before downloading your completed lab.";
      nameControl.focus();
      return;
    }
    button.disabled = true;
    if (status) status.textContent = "Preparing your filled HTML copy…";
    try {
      if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
        try { await window.MathJax.startup.promise; } catch (_) {}
      }
      const copy = main.cloneNode(true);
      freezeResponses(main, copy);
      cleanSubmission(copy);
      await embedPictures(copy);
      const css = await pageStyles();
      const labTitle = main.querySelector("h1")?.textContent.trim() || document.title;
      const savedAt = new Date().toLocaleString();
      const cover = document.createElement("div");
      cover.className = "submission-cover";
      const title = document.createElement("h2");
      title.textContent = "Completed laboratory";
      const who = document.createElement("p");
      who.textContent = "Student: " + student;
      const lesson = document.createElement("p");
      lesson.textContent = "Activity: " + labTitle;
      const date = document.createElement("p");
      date.textContent = "Saved: " + savedAt;
      cover.append(title, who, lesson, date);
      copy.prepend(cover);
      const html = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">' +
        '<meta name="viewport" content="width=device-width,initial-scale=1">' +
        '<title>' + escapeHTML(labTitle + " — " + student) + '</title>' +
        '<style>' + css.replace(/<\/style/gi, '<\\/style') + '\n' + presentationStyle + '</style>' +
        '</head><body class="lab-focus">' + copy.outerHTML + '</body></html>';
      const blob = new Blob([html], {type:"text/html;charset=utf-8"});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      const originalFile = window.location.pathname.split("/").pop().replace(/\.html$/i, "");
      link.href = url;
      link.download = "Math107_" + originalFile + "_" + safeName(student) + ".html";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(function () { URL.revokeObjectURL(url); }, 2000);
      if (status) status.textContent = "Downloaded a filled HTML copy. Your browser autosave is unchanged.";
    } catch (error) {
      if (status) status.textContent = "Couldn't prepare the HTML copy. Try again or use Print / save.";
      if (typeof console !== "undefined") console.error("Lab HTML download failed", error);
    } finally {
      button.disabled = false;
    }
  }

  function init() {
    const button = document.querySelector("[data-download-filled-html]");
    if (button) button.addEventListener("click", function () { downloadFilledLab(button); });
  }

  if (typeof module === "object" && module.exports) {
    module.exports = {safeName, escapeHTML, responseText};
  }
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();
  }
})();
