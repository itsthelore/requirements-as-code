/**
 * Types for the `lore export` JSON payload the viewer consumes.
 * The schema is a PROPOSAL — see lore-web/VIEWER_CONTRACT.md.
 */

export interface CorpusMeta {
  /** Human-readable corpus name, e.g. the repository name. */
  name: string;
  /** ISO 8601 timestamp of when the export was generated. */
  generated_at: string;
  /** Version of the Lore CLI that produced the export. */
  lore_version: string;
  /** True when the corpus is demonstration data, not a real repo. */
  sample?: boolean;
}

export interface Artifact {
  /** Stable artifact ID, e.g. "ADR-014". Unique within the corpus. */
  id: string;
  /** Artifact family, e.g. "adr", "standard". Open set. */
  type: string;
  /** Lifecycle status, e.g. "accepted", "superseded". Open set. */
  status: string;
  title: string;
  /** Body rendered to HTML at export time. Trusted — see contract. */
  body_html: string;
}

export interface Relationship {
  /** Source artifact ID; the edge reads "<from> <type> <to>". */
  from: string;
  to: string;
  /** Edge type, e.g. "supersedes" | "refines" | "relates-to" | "implements". */
  type: string;
}

export interface LoreExport {
  schema_version: number;
  corpus: CorpusMeta;
  artifacts: Artifact[];
  relationships: Relationship[];
}
