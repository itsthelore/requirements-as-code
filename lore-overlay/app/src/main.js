// Minimal two-gate capture UI. Authored scaffold — needs a bundler (e.g. Vite)
// to resolve the @tauri-apps/api import; see ../../README.md.
import { invoke } from "@tauri-apps/api/core";

const $ = (id) => document.getElementById(id);
let current = null; // the proposed { artifact_type, title, body }

$("propose").addEventListener("click", async () => {
  const intent = $("intent").value.trim();
  if (!intent) return;
  setResult("Drafting…");
  try {
    // Gate 1 prep: propose. No file is written yet.
    current = await invoke("propose", { artifactType: "decision", intent });
    $("title").value = current.title;
    $("body").value = current.body; // the textarea stays the source of truth
    showPreview(); // default to the rendered view
    $("capture").hidden = true;
    $("review").hidden = false;
    setResult("");
  } catch (e) {
    setResult("Couldn't draft: " + e);
  }
});

$("back").addEventListener("click", () => {
  $("review").hidden = true;
  $("capture").hidden = false;
});

// --- Body view toggle: rendered "Preview" (default) vs raw "Edit" -----------

function showPreview() {
  $("body-preview").innerHTML = renderMarkdown($("body").value);
  $("body-preview").hidden = false;
  $("body").hidden = true;
  $("tab-preview").setAttribute("aria-selected", "true");
  $("tab-edit").setAttribute("aria-selected", "false");
}

function showEdit() {
  $("body").hidden = false;
  $("body-preview").hidden = true;
  $("tab-edit").setAttribute("aria-selected", "true");
  $("tab-preview").setAttribute("aria-selected", "false");
  $("body").focus();
}

$("tab-preview").addEventListener("click", showPreview);
$("tab-edit").addEventListener("click", showEdit);

// Minimal, dependency-free markdown → HTML. Artifact content is untrusted
// (ADR-065), so escape first, then apply a small, safe subset.
function renderMarkdown(src) {
  const esc = src.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[c]);
  const inline = (s) =>
    s
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>");
  let html = "";
  let list = null;
  let para = [];
  const closeList = () => {
    if (list) {
      html += `</${list}>`;
      list = null;
    }
  };
  const flushPara = () => {
    if (para.length) {
      html += `<p>${inline(para.join(" "))}</p>`;
      para = [];
    }
  };
  for (const line of esc.split("\n")) {
    let m;
    if (/^\s*$/.test(line)) {
      flushPara();
      closeList();
    } else if ((m = line.match(/^(#{1,6})\s+(.*)$/))) {
      flushPara();
      closeList();
      html += `<h${m[1].length}>${inline(m[2])}</h${m[1].length}>`;
    } else if ((m = line.match(/^\s*[-*]\s+(.*)$/))) {
      flushPara();
      if (list !== "ul") {
        closeList();
        html += "<ul>";
        list = "ul";
      }
      html += `<li>${inline(m[1])}</li>`;
    } else if ((m = line.match(/^\s*\d+\.\s+(.*)$/))) {
      flushPara();
      if (list !== "ol") {
        closeList();
        html += "<ol>";
        list = "ol";
      }
      html += `<li>${inline(m[1])}</li>`;
    } else {
      closeList();
      para.push(line.trim());
    }
  }
  flushPara();
  closeList();
  return html;
}

$("publish").addEventListener("click", async () => {
  if (!current) return;
  const title = $("title").value.trim();
  const body = $("body").value;
  const slug = title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "")
    .slice(0, 60);
  setResult("Opening a draft pull request…");
  try {
    // Gate 2 prep: write + validate + open a DRAFT PR (independent merge lands it).
    const outcome = await invoke("publish", {
      artifactType: current.artifact_type,
      title,
      body,
      destPath: `rac/decisions/${slug}.md`,
      branch: `capture/${slug}`,
      coauthor: null,
    });
    setResult(`Proposed as ${outcome.minted_id} — review & merge: ${outcome.pr_url}`);
  } catch (e) {
    setResult("Couldn't publish: " + e);
  }
});

function setResult(msg) {
  $("result").textContent = msg;
}
