# Add a Skill

1. Create `skills/<new-skill-name>/SKILL.md`, with frontmatter `name` and `description`.
2. Add `agents/openai.yaml` and only useful optional references, scripts, assets and tests.
3. Keep each Skill self-contained, update the root README index and changelog, and run relevant tests.
4. Scan every file for API keys, passwords, personal contact details, patient data, manuscript drafts, editorial correspondence and unapproved material before committing.
5. Update the collection plugin manifest when packaging a new plugin release. GitHub commits do not automatically publish a ChatGPT plugin.
