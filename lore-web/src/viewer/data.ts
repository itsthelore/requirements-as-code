/**
 * Data loading and indexing for the export viewer.
 *
 * Loading strategy (see VIEWER_CONTRACT.md):
 *   1. If the document contains <script type="application/json"
 *      id="lore-export">, parse it. This is how the built single-file
 *      artifact works from file:// with zero network requests.
 *   2. Otherwise (dev server / hosted multi-page build), fetch the
 *      committed sample corpus as an asset.
 */

import type { Artifact, LoreExport, Relationship } from './types';

export async function loadExport(): Promise<LoreExport> {
  const inline = document.getElementById('lore-export');
  const text = inline?.textContent?.trim();
  if (text) {
    return JSON.parse(text) as LoreExport;
  }
  const url = new URL('./sample/lore-export.sample.json', import.meta.url);
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`failed to load sample export (${res.status})`);
  }
  return (await res.json()) as LoreExport;
}

/** One artifact plus everything precomputed for list/search/detail. */
export interface IndexedArtifact {
  artifact: Artifact;
  /** Lowercased id + title + body text, computed once for search. */
  haystack: string;
}

export interface CorpusIndex {
  data: LoreExport;
  rows: IndexedArtifact[];
  byId: Map<string, Artifact>;
  /** Distinct artifact types, in first-seen order. */
  types: string[];
  /** Distinct statuses, in first-seen order. */
  statuses: string[];
  outbound: Map<string, Relationship[]>;
  inbound: Map<string, Relationship[]>;
  /** Set of all artifact IDs, for cited-ID linkification. */
  idSet: Set<string>;
}

const TAG_RE = /<[^>]*>/g;
const WS_RE = /\s+/g;

export function buildIndex(data: LoreExport): CorpusIndex {
  const byId = new Map<string, Artifact>();
  const types: string[] = [];
  const statuses: string[] = [];
  const rows: IndexedArtifact[] = [];

  for (const artifact of data.artifacts) {
    byId.set(artifact.id, artifact);
    if (!types.includes(artifact.type)) types.push(artifact.type);
    if (!statuses.includes(artifact.status)) statuses.push(artifact.status);
    const bodyText = artifact.body_html.replace(TAG_RE, ' ').replace(WS_RE, ' ');
    rows.push({
      artifact,
      haystack: `${artifact.id} ${artifact.title} ${bodyText}`.toLowerCase(),
    });
  }

  const outbound = new Map<string, Relationship[]>();
  const inbound = new Map<string, Relationship[]>();
  for (const edge of data.relationships) {
    const out = outbound.get(edge.from);
    if (out) out.push(edge);
    else outbound.set(edge.from, [edge]);
    const inn = inbound.get(edge.to);
    if (inn) inn.push(edge);
    else inbound.set(edge.to, [edge]);
  }

  return {
    data,
    rows,
    byId,
    types,
    statuses,
    outbound,
    inbound,
    idSet: new Set(byId.keys()),
  };
}

/**
 * Replace occurrences of known artifact IDs inside the rendered body
 * with links to their detail view. Walks text nodes only; existing
 * anchors are left alone, and tokens that do not match a corpus ID are
 * untouched.
 */
const ID_TOKEN_RE = /\b[A-Z][A-Z0-9]{1,11}-\d{1,6}\b/g;

export function linkifyIds(root: HTMLElement, idSet: Set<string>): void {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      let el = node.parentElement;
      while (el && el !== root) {
        if (el.tagName === 'A') return NodeFilter.FILTER_REJECT;
        el = el.parentElement;
      }
      return NodeFilter.FILTER_ACCEPT;
    },
  });

  const textNodes: Text[] = [];
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    textNodes.push(n as Text);
  }

  for (const textNode of textNodes) {
    const text = textNode.nodeValue ?? '';
    ID_TOKEN_RE.lastIndex = 0;
    let match: RegExpExecArray | null;
    let last = 0;
    let frag: DocumentFragment | null = null;
    while ((match = ID_TOKEN_RE.exec(text)) !== null) {
      if (!idSet.has(match[0])) continue;
      frag ??= document.createDocumentFragment();
      if (match.index > last) {
        frag.appendChild(document.createTextNode(text.slice(last, match.index)));
      }
      const a = document.createElement('a');
      a.href = `#/artifact/${encodeURIComponent(match[0])}`;
      a.textContent = match[0];
      frag.appendChild(a);
      last = match.index + match[0].length;
    }
    if (frag) {
      if (last < text.length) {
        frag.appendChild(document.createTextNode(text.slice(last)));
      }
      textNode.replaceWith(frag);
    }
  }
}
