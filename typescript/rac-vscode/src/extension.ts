/**
 * RAC VS Code / Cursor extension.
 *
 * Wires the `@rac/sdk` thin client to the editor. All analysis stays in `rac`
 * (ADR-063); this extension maps its output into the editor:
 *
 *  - per-file validation diagnostics, live as you type (the unsaved buffer is
 *    piped through `rac validate -`), debounced, plus immediately on open/save;
 *  - cross-artifact enforcement: broken and retired-target references surfaced
 *    at the reference site, from `rac relationships --validate` (refreshed on
 *    save/activation, since relationship validation reads files from disk);
 *  - hover and go-to-definition on artifact IDs / aliases via `rac resolve`.
 */

import * as path from "node:path";

import * as vscode from "vscode";

import {
  RacClient,
  RacNotFoundError,
  isResolved,
  type FileValidation,
  type Issue,
  type RelationshipIssue,
  type RelationshipValidation,
  type ResolvedArtifact,
} from "@rac/sdk";

const DEBOUNCE_MS = 300;
const RELATIONSHIP_DEBOUNCE_MS = 600;

let diagnostics: vscode.DiagnosticCollection;
let relationshipDiagnostics: vscode.DiagnosticCollection;
const clients = new Map<string, RacClient>();
const debounce = new Map<string, ReturnType<typeof setTimeout>>();
const relationshipDebounce = new Map<string, ReturnType<typeof setTimeout>>();
let warnedMissing = false;

export function activate(context: vscode.ExtensionContext): void {
  diagnostics = vscode.languages.createDiagnosticCollection("rac");
  relationshipDiagnostics = vscode.languages.createDiagnosticCollection("rac-relationships");
  const selector: vscode.DocumentSelector = { language: "markdown", scheme: "file" };

  context.subscriptions.push(
    diagnostics,
    relationshipDiagnostics,
    vscode.workspace.onDidOpenTextDocument((doc) => void validateDocument(doc)),
    vscode.workspace.onDidSaveTextDocument((doc) => {
      void validateDocument(doc);
      scheduleRelationshipsFor(doc);
    }),
    vscode.workspace.onDidChangeTextDocument((e) => scheduleValidate(e.document)),
    vscode.workspace.onDidCloseTextDocument((doc) => {
      cancelScheduled(doc);
      diagnostics.delete(doc.uri);
    }),
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration("rac")) {
        clients.clear();
        void validateWorkspace();
        refreshAllRelationships();
      }
    }),
    vscode.commands.registerCommand("rac.validateWorkspace", validateWorkspace),
    vscode.languages.registerHoverProvider(selector, { provideHover }),
    vscode.languages.registerDefinitionProvider(selector, { provideDefinition }),
  );

  for (const doc of vscode.workspace.textDocuments) void validateDocument(doc);
  refreshAllRelationships();
}

export function deactivate(): void {
  for (const timer of debounce.values()) clearTimeout(timer);
  for (const timer of relationshipDebounce.values()) clearTimeout(timer);
  debounce.clear();
  relationshipDebounce.clear();
  diagnostics?.clear();
  diagnostics?.dispose();
  relationshipDiagnostics?.clear();
  relationshipDiagnostics?.dispose();
}

// --- per-file validation ----------------------------------------------------

function isEnabled(): boolean {
  return vscode.workspace
    .getConfiguration("rac")
    .get<boolean>("validate.enable", true);
}

function scheduleValidate(doc: vscode.TextDocument): void {
  const key = doc.uri.toString();
  const existing = debounce.get(key);
  if (existing) clearTimeout(existing);
  debounce.set(
    key,
    setTimeout(() => {
      debounce.delete(key);
      void validateDocument(doc);
    }, DEBOUNCE_MS),
  );
}

function cancelScheduled(doc: vscode.TextDocument): void {
  const key = doc.uri.toString();
  const existing = debounce.get(key);
  if (existing) {
    clearTimeout(existing);
    debounce.delete(key);
  }
}

async function validateDocument(doc: vscode.TextDocument): Promise<void> {
  if (!isEnabled()) return;
  if (doc.languageId !== "markdown" || doc.uri.scheme !== "file") return;
  if (!looksLikeRacArtifact(doc.getText())) {
    diagnostics.delete(doc.uri);
    return;
  }
  const folder = vscode.workspace.getWorkspaceFolder(doc.uri);
  if (!folder) return;

  try {
    // Validate the current buffer (unsaved edits included) via stdin.
    const result = await clientFor(folder).validateText(doc.getText());
    diagnostics.set(doc.uri, toDiagnostics(result));
  } catch (err) {
    if (err instanceof RacNotFoundError) {
      warnMissingOnce();
      return;
    }
    console.error("RAC: validation failed", err);
  }
}

function toDiagnostics(result: FileValidation): vscode.Diagnostic[] {
  return [...result.errors, ...result.warnings].map(issueToDiagnostic);
}

function issueToDiagnostic(issue: Issue): vscode.Diagnostic {
  // rac lines are 1-based; null means file-level (anchor at the first line).
  const line = issue.line && issue.line > 0 ? issue.line - 1 : 0;
  const range = new vscode.Range(line, 0, line, Number.MAX_SAFE_INTEGER);
  const diagnostic = new vscode.Diagnostic(
    range,
    issue.message,
    issue.severity === "error"
      ? vscode.DiagnosticSeverity.Error
      : vscode.DiagnosticSeverity.Warning,
  );
  diagnostic.source = "rac";
  diagnostic.code = issue.code;
  return diagnostic;
}

async function validateWorkspace(): Promise<void> {
  for (const doc of vscode.workspace.textDocuments) {
    await validateDocument(doc);
  }
  refreshAllRelationships();
}

// --- cross-artifact enforcement ---------------------------------------------

// Severity and message per relationship-validation code. The headline split:
// a reference that does not resolve (error) vs. a reference to a retired
// (superseded/deprecated) artifact (warning) — the latter is what makes the
// extension RAC, not a generic linter (ADR-049, ADR-051).
const RELATIONSHIP_SEVERITY: Record<string, vscode.DiagnosticSeverity> = {
  "relationship-target-not-found": vscode.DiagnosticSeverity.Error,
  "relationship-target-ambiguous": vscode.DiagnosticSeverity.Error,
  "relationship-cycle": vscode.DiagnosticSeverity.Error,
  "relationship-target-type-mismatch": vscode.DiagnosticSeverity.Warning,
  "relationship-target-superseded": vscode.DiagnosticSeverity.Warning,
  "relationship-self-reference": vscode.DiagnosticSeverity.Warning,
  "relationship-edge-unsupported": vscode.DiagnosticSeverity.Warning,
};

const RELATIONSHIP_MESSAGE: Record<string, string> = {
  "relationship-target-not-found": "Reference does not resolve",
  "relationship-target-ambiguous": "Ambiguous reference (matches multiple artifacts)",
  "relationship-cycle": "Relationship cycle through",
  "relationship-target-type-mismatch": "Reference resolves to the wrong artifact type",
  "relationship-target-superseded": "References a retired (superseded/deprecated) artifact",
  "relationship-self-reference": "Artifact references itself",
  "relationship-edge-unsupported": "Unsupported relationship for this artifact type",
};

function scheduleRelationshipsFor(doc: vscode.TextDocument): void {
  if (doc.languageId !== "markdown" || doc.uri.scheme !== "file") return;
  if (!looksLikeRacArtifact(doc.getText())) return;
  const folder = vscode.workspace.getWorkspaceFolder(doc.uri);
  if (folder) scheduleRelationships(folder);
}

function scheduleRelationships(folder: vscode.WorkspaceFolder): void {
  const key = folder.uri.fsPath;
  const existing = relationshipDebounce.get(key);
  if (existing) clearTimeout(existing);
  relationshipDebounce.set(
    key,
    setTimeout(() => {
      relationshipDebounce.delete(key);
      void refreshRelationships(folder);
    }, RELATIONSHIP_DEBOUNCE_MS),
  );
}

function refreshAllRelationships(): void {
  for (const folder of vscode.workspace.workspaceFolders ?? []) {
    void refreshRelationships(folder);
  }
}

async function refreshRelationships(folder: vscode.WorkspaceFolder): Promise<void> {
  if (!isEnabled()) return;
  let result: RelationshipValidation;
  try {
    // Relationship validation reads files from disk, so it reflects the saved
    // corpus (not unsaved buffers) — hence save/activation-triggered.
    result = await clientFor(folder).validateRelationships(folder.uri.fsPath);
  } catch (err) {
    if (err instanceof RacNotFoundError) warnMissingOnce();
    else console.error("RAC: relationship validation failed", err);
    return;
  }

  const byFile = new Map<string, RelationshipIssue[]>();
  for (const issue of result.issues) {
    const list = byFile.get(issue.source_path) ?? [];
    list.push(issue);
    byFile.set(issue.source_path, list);
  }

  relationshipDiagnostics.clear();
  for (const [source, issues] of byFile) {
    const uri = path.isAbsolute(source)
      ? vscode.Uri.file(source)
      : vscode.Uri.joinPath(folder.uri, source);
    let doc: vscode.TextDocument;
    try {
      doc = await vscode.workspace.openTextDocument(uri);
    } catch {
      continue; // a referenced source we cannot open — skip rather than guess.
    }
    relationshipDiagnostics.set(
      uri,
      issues.map((issue) => relationshipDiagnostic(doc, issue)),
    );
  }
}

function relationshipDiagnostic(
  doc: vscode.TextDocument,
  issue: RelationshipIssue,
): vscode.Diagnostic {
  const range = findReferenceRange(doc, issue.relationship, issue.target);
  const label = RELATIONSHIP_MESSAGE[issue.code] ?? "Relationship issue";
  const severity = RELATIONSHIP_SEVERITY[issue.code] ?? vscode.DiagnosticSeverity.Warning;
  const diagnostic = new vscode.Diagnostic(range, `${label}: ${issue.target}`, severity);
  diagnostic.source = "rac";
  diagnostic.code = issue.code;
  return diagnostic;
}

// Relationship issues carry no line, so anchor the diagnostic on the target
// token inside the declared relationship section (e.g. "## Related Decisions"),
// falling back to the section heading, then the file head.
function findReferenceRange(
  doc: vscode.TextDocument,
  relationship: string,
  target: string,
): vscode.Range {
  const lines = doc.getText().split(/\r?\n/);
  const heading = relationshipHeading(relationship);
  const headingRe = new RegExp(`^#{1,6}\\s+${escapeRegExp(heading)}\\s*$`, "i");
  const headingIdx = lines.findIndex((line) => headingRe.test(line));

  const from = headingIdx >= 0 ? headingIdx + 1 : 0;
  for (let i = from; i < lines.length; i++) {
    if (headingIdx >= 0 && /^#{1,6}\s+/.test(lines[i])) break; // next heading ends the section
    const col = lines[i].indexOf(target);
    if (col >= 0) return new vscode.Range(i, col, i, col + target.length);
  }
  if (headingIdx >= 0) {
    return new vscode.Range(headingIdx, 0, headingIdx, lines[headingIdx].length);
  }
  return new vscode.Range(0, 0, 0, Number.MAX_SAFE_INTEGER);
}

function relationshipHeading(relationship: string): string {
  // "related_requirements" -> "Related Requirements"
  return relationship
    .split("_")
    .map((word) => (word ? word[0].toUpperCase() + word.slice(1) : word))
    .join(" ");
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// --- hover & go-to-definition ----------------------------------------------

// Reference-ish tokens: identifiers with a hyphen (adr-007, v0.20.0-foo,
// rac-growth-adoption) or a RAC/REQ id. A cheap filter so plain prose words
// don't each trigger a `rac resolve`.
const REFERENCE_WORD = /[A-Za-z0-9][A-Za-z0-9._-]*[A-Za-z0-9]/;
function looksLikeReference(token: string): boolean {
  return token.includes("-") && /[A-Za-z]/.test(token);
}

async function resolveAt(
  doc: vscode.TextDocument,
  position: vscode.Position,
): Promise<ResolvedArtifact | undefined> {
  if (!looksLikeRacArtifact(doc.getText())) return undefined;
  const folder = vscode.workspace.getWorkspaceFolder(doc.uri);
  if (!folder) return undefined;
  const range = doc.getWordRangeAtPosition(position, REFERENCE_WORD);
  if (!range) return undefined;
  const token = doc.getText(range);
  if (!looksLikeReference(token)) return undefined;

  try {
    const result = await clientFor(folder).resolve(token);
    return isResolved(result) ? result : undefined;
  } catch (err) {
    if (err instanceof RacNotFoundError) warnMissingOnce();
    return undefined;
  }
}

async function provideHover(
  doc: vscode.TextDocument,
  position: vscode.Position,
): Promise<vscode.Hover | undefined> {
  const target = await resolveAt(doc, position);
  if (!target) return undefined;
  const md = new vscode.MarkdownString(undefined, true);
  md.appendMarkdown(`**${target.title}**\n\n`);
  md.appendMarkdown(`\`${target.type}\` · \`${target.id}\`\n\n`);
  md.appendMarkdown(`[${target.path}](${vscode.Uri.file(target.path)})`);
  return new vscode.Hover(md);
}

async function provideDefinition(
  doc: vscode.TextDocument,
  position: vscode.Position,
): Promise<vscode.Location | undefined> {
  const target = await resolveAt(doc, position);
  if (!target) return undefined;
  const folder = vscode.workspace.getWorkspaceFolder(doc.uri);
  if (!folder) return undefined;
  // resolve returns a path relative to the client cwd (the workspace folder).
  const uri = vscode.Uri.joinPath(folder.uri, target.path);
  return new vscode.Location(uri, new vscode.Position(0, 0));
}

// --- shared -----------------------------------------------------------------

function clientFor(folder: vscode.WorkspaceFolder): RacClient {
  const key = folder.uri.fsPath;
  let client = clients.get(key);
  if (!client) {
    const configured = vscode.workspace
      .getConfiguration("rac", folder.uri)
      .get<string>("path")
      ?.trim();
    client = new RacClient({
      racPath: configured ? configured : undefined,
      cwd: folder.uri.fsPath,
    });
    clients.set(key, client);
  }
  return client;
}

// Only treat Markdown with a leading YAML frontmatter block carrying
// `schema_version` as a RAC artifact. A routing gate, not classification.
const FRONTMATTER = /^---\r?\n([\s\S]*?)\r?\n---/;
function looksLikeRacArtifact(text: string): boolean {
  const match = FRONTMATTER.exec(text);
  return match !== null && /(^|\n)\s*schema_version\s*:/.test(match[1] ?? "");
}

function warnMissingOnce(): void {
  if (warnedMissing) return;
  warnedMissing = true;
  void vscode.window
    .showWarningMessage(
      "RAC: the `rac` CLI was not found. Install it (pip install requirements-as-code) " +
        "or set `rac.path` in settings.",
      "Open Settings",
    )
    .then((choice) => {
      if (choice === "Open Settings") {
        void vscode.commands.executeCommand(
          "workbench.action.openSettings",
          "rac.path",
        );
      }
    });
}
