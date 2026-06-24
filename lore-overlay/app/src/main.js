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
    $("body").value = current.body;
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
