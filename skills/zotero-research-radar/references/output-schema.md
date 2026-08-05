# JSON Output

`radar recommend --format json` emits one object with `generated_at`, `query`, and `papers`.

Each paper has a stable `id` (`source:url`), `title`, `authors`, `abstract`, nullable `score`, nullable `summary`, nullable `affiliations`, `source_url`, and nullable `pdf_url`.

Treat `summary` and `affiliations` as optional because they require `--summarize` and an LLM configuration. Preserve `id`, source URL, and score in user-facing answers.
