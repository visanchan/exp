# Repository Skills

Working methods that travel with a clone of this repository. No installation, no
dependency on any particular machine or account — clone the repo and they are
there.

Point your AI tool at `AGENTS.md` first; it is authoritative and wins over
anything here.

## What is here

| Skill | Use it when |
|---|---|
| [`ai-class-operating-partner`](ai-class-operating-partner/SKILL.md) | Turning a class task into a defined, tested experiment with the learning preserved. The default for repository work. |
| [`local-dev-servers`](local-dev-servers/SKILL.md) | An app needs a backend and a frontend running at once, a dev server will not stay up under an agent, or a `localhost` URL will not open. |
| [`debug-mantra`](debug-mantra/SKILL.md) | Something is broken, throwing or failing — especially after two or three attempted fixes have already missed. Recite the mantra, then work the four steps in order. |
| [`reviewing-ai-written-code`](reviewing-ai-written-code/SKILL.md) | Before keeping, committing, or approving code an agent wrote. |
| [`session-handoff`](session-handoff/SKILL.md) | A session is ending or straining, or work is passing to another agent or person. |
| [`business-analysis`](business-analysis/SKILL.md) | Deciding whether something is worth doing, comparing options, working out unit economics or a break-even, or presenting numbers someone has to act on. |
| [`market-sizing`](market-sizing/SKILL.md) | Estimating how big an opportunity is — TAM, SAM, SOM — so the number survives being questioned. |
| [`requirements-workbook`](requirements-workbook/SKILL.md) | Before building something whose requirements live in someone's head — generates a plain-language HTML questionnaire, opens it, and takes the pasted answers back as the spec. |
| [`write-a-repo-skill`](write-a-repo-skill/SKILL.md) | A working method has proven itself often enough to be worth capturing here. |

## Using them

Most agents discover `.agents/skills/` automatically. If yours does not, point
it at the file directly — they are plain markdown and readable on their own.

To invoke one explicitly:

```text
Use $debug-mantra — the login test passes locally and fails in CI.
```

## What is deliberately not here

These skills are **synthesized, not copied**. They cover reusable methods; they
are not backups of anyone's installed skill collection.

Excluded on purpose:

- **Private context** — business rules, customer data, personal projects,
  account or board specifics. None of it belongs in a shared repository.
- **Third-party skill text** — redistribution rights are usually unknown. Where
  an external method was worth keeping, the *idea* was rewritten from scratch;
  the text was not copied.
- **Machine-specific setup** — anything depending on one person's paths,
  installed tools, or credentials.

The reasoning is recorded in
[`../../docs/decisions/`](../../docs/decisions/) and the boundaries in
[`ai-class-operating-partner/references/provenance-and-scope.md`](ai-class-operating-partner/references/provenance-and-scope.md).

## Adding one

Read [`write-a-repo-skill`](write-a-repo-skill/SKILL.md). It covers the layout,
the frontmatter, the privacy and provenance check, and where to register the new
skill so it is discoverable.
