import type { Artifact } from './types';

/**
 * Small bordered chips for artifact type and status.
 * Colour is semantic only: accepted = green (pass), rejected = error,
 * superseded/deprecated = muted. Everything else is plain text.
 */

const STATUS_CLASS: Record<string, string> = {
  accepted: 'viewer-chip--accepted',
  rejected: 'viewer-chip--rejected',
  superseded: 'viewer-chip--muted',
  deprecated: 'viewer-chip--muted',
};

export function TypeChip({ type }: { type: string }) {
  return <span className="viewer-chip viewer-chip--type">{type}</span>;
}

export function StatusChip({ status }: { status: string }) {
  const semantic = STATUS_CLASS[status] ?? '';
  return (
    <span className={`viewer-chip${semantic ? ` ${semantic}` : ''}`}>
      {status}
    </span>
  );
}

export function ArtifactChips({ artifact }: { artifact: Artifact }) {
  return (
    <span className="viewer-chips">
      <TypeChip type={artifact.type} />
      <StatusChip status={artifact.status} />
    </span>
  );
}
