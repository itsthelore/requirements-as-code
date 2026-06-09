# Design: Explorer Editor Integration

## Status

Proposed

## Purpose

Define how Explorer integrates with external editing environments.

Explorer identifies findings.

External tools perform authoring and modification.

## Design Principles

### Existing Tools First

Users should continue using their preferred editor.

Examples include:

- Cursor
- VS Code
- Windsurf
- Vim
- Neovim
- Emacs
- JetBrains IDEs

### Explorer Is Not An Editor

Explorer shall not implement:

- text editing
- document authoring
- content management

### Fast Transition

Opening an artifact should require minimal user effort.

## Configuration

Explorer shall support a configured default editor.

Example:

```yaml
explorer:
  editor:
    command: cursor
```

## First Run Experience

Users may select a preferred editor during onboarding.

Editor configuration should be modifiable later.

## Open Behaviour

Explorer should support:

### Open Artifact

Open artifact directly.

### Open Artifact At Location

Future enhancement.

### Open Multiple Artifacts

Future enhancement.

## Fallback Behaviour

If no editor is configured:

- prompt user
- use system default editor
- provide configuration guidance

## Related Artifacts

- DESIGN-first-run-experience
- DESIGN-action-workflows