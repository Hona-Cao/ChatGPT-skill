# ChatGPT Skills

此仓库用于集中管理个人 ChatGPT / Codex Skills。每个 Skill 放在 `skills/<skill-name>/` 下，以便独立维护。

## Skills

| Skill | Version | Description |
| --- | --- | --- |
| [Clinical Manuscript Writing & Scientific Audit](skills/clinical-manuscript-audit/SKILL.md) | 1.1.0 | Medical manuscript writing, statistical checks, reporting guidelines, Major Revision and reviewer responses |

## Layout

- `skills/<skill-name>/SKILL.md`: required Skill entry point.
- `skills/<skill-name>/agents/openai.yaml`: UI metadata.
- `skills/<skill-name>/references/`: guidance and workflows.
- `skills/<skill-name>/scripts/`: local audit utilities.
- `skills/<skill-name>/tests/`: tests.
- `skills/<skill-name>/assets/`: blank templates and reusable assets.
- `docs/ADD_A_SKILL.md`: instructions for future Skills.
- `.codex-plugin/plugin.json`: optional collection-level plugin manifest.

## Use

Read the [Skill instructions](skills/clinical-manuscript-audit/SKILL.md) or package the individual Skill folder for an available Skills upload interface. The root manifest is for compatible Plugin packaging, which may have different ZIP structure requirements.

Existing [ChatGPT plugin](https://chatgpt.com/plugins/Plugin_2b84b819b2c881919a3f4e0a6cb025e3) is version 1.1.0. **GitHub pushes do not automatically update installed ChatGPT plugins.**

## Test

```bash
python -m unittest discover -s skills/clinical-manuscript-audit/tests -v
```

## Privacy

Only source code, guidelines and **blank templates** belong in this public repository. Do not commit patient data, manuscripts, reviewer emails, institutional documents, credentials or unapproved research results.

## License

No open-source license selected yet. Public visibility does not grant a reuse license; repository owner may add a chosen license later.
