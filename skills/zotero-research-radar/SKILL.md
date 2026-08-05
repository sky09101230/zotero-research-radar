---
name: zotero-research-radar
description: Generate, interpret, and track personalized literature recommendations from a local Zotero library through the `radar` CLI. Use when a user asks for recent papers relevant to their Zotero collections, a weekly literature report, feedback on recommended papers, or validation of the local Zotero literature-radar setup.
---

# Zotero Research Radar

Run the repository CLI and base all recommendations on its structured JSON output. Do not import its internal Python objects from an agent task.

## Workflow

1. Run `uv run radar doctor` before the first live recommendation. Report missing configuration without inventing credentials.
2. For personalized recommendations or a report, run:

```powershell
uv run radar recommend --format json --output reports/radar.json
```

Use `--set executor.source=[arxiv]` only when the user specifies a source. Use `--include-seen` only when the user requests previously recommended papers. Use `--summarize` only when LLM credentials are configured and a generated summary is useful.

3. Read the JSON file. If the user asks for a human report, synthesize rather than copying each abstract. Preserve every paper's `id`, source URL, score, and uncertainty about missing summaries.
4. Record explicit feedback with:

```powershell
uv run radar feedback accept "arxiv:https://example.org/paper"
```

Use only `accept`, `reject`, `later`, or `seen`. Do not claim feedback changes ranking until the engine implements a feedback ranker.

## Outputs

Read [references/output-schema.md](references/output-schema.md) before interpreting the JSON contract or integrating another tool.

Use [scripts/run_radar.py](scripts/run_radar.py) only as a thin wrapper when the calling environment needs a Python entry point.
