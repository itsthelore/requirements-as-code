// Minimal two-gate capture UI. Authored scaffold — needs a bundler (e.g. Vite)
// to resolve the bare-module imports; see ../../README.md.
import { invoke } from "@tauri-apps/api/core";
import MarkdownIt from "markdown-it";
import DOMPurify from "dompurify";

// Full CommonMark rendering for the body preview. `html: false` escapes any raw
// HTML embedded in the artifact rather than passing it through, and the output is
// run through DOMPurify before it touches innerHTML — artifact content is
// untrusted input (ADR-065), so the render path must not become an injection
// vector. `linkify` turns bare URLs into links; markdown-it's own validateLink
// already blocks javascript:/vbscript:/data: schemes.
const md = new MarkdownIt({ html: false, linkify: true, typographer: true });

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

// CommonMark → sanitized HTML for the rendered body view.
function renderMarkdown(src) {
  return DOMPurify.sanitize(md.render(src));
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
