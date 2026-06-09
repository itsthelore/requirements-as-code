# Requirements as Code

> **Treat product knowledge like source code.**

RAC is a command-line tool for managing requirements, decisions, roadmaps, prompts,
and design artifacts as plain Markdown, right inside your Git repository.

```bash
pip install requirements-as-code
```

## What is RAC?

The code is structured, the tests are automated, the infrastructure is versioned —
but the *reasoning* behind what you build is scattered across documents, tickets,
chats, and AI conversations. RAC brings that knowledge back into the repository.

You write product thinking in Markdown; RAC validates it, inspects it, and connects
it — so it stays durable, reviewable, and usable as context for both humans and AI.
No proprietary formats, no hosted platform, no lock-in.

## Who is it for?

- **Software and product teams** who want the *why* behind their software versioned
  alongside the code.
- **AI-native teams** who need structured, durable context instead of more scattered
  chat history.

## Install

Requires Python 3.11+.

```bash
pip install requirements-as-code
# or
uv tool install requirements-as-code
```

## Quick Start

```bash
rac validate requirement.md   # check one artifact
rac inspect requirement.md    # see its type and completeness
rac stats rac/                # summarize a directory of artifacts
```

New to RAC? Walk through your first artifact in five minutes:
**[docs/quickstart.md](docs/quickstart.md)**.

## Supported Artifact Types

- **Requirements** — what needs to exist
- **Decisions** — why choices were made (ADRs)
- **Roadmaps** — where the product is heading
- **Prompts** — reusable AI collaboration patterns
- **Designs** — product experience thinking

Everything stays plain Markdown — see **[docs/artifacts.md](docs/artifacts.md)**.

## Documentation

- [Quickstart](docs/quickstart.md) — install and try RAC in five minutes
- [CLI reference](docs/cli.md) — every command, flag, and exit code
- [Artifact types](docs/artifacts.md) — the five types and their sections
- [Relationships](docs/relationships.md) — link artifacts and validate the links
- [Repository workflow](docs/repo-workflow.md) — organize a repo with RAC
- [Testing & contributing](docs/testing.md) — local setup and verification
- [Examples](docs/examples.md) — small, realistic artifacts

## Project Status

RAC is early and evolving quickly. A terminal Explorer for browsing your knowledge
base is planned. Contributions, ideas, and experiments are welcome.

## License

MIT
