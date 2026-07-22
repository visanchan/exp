---
name: write-a-repo-skill
description: Write a new repository-local skill, or improve an existing one, so it travels with a clone and stays safe to share. Use when a working method has been repeated enough to be worth capturing, when an agent keeps needing the same correction, or when adapting an external skill for this repository. Covers what deserves to be a skill, the file layout and frontmatter this repository uses, writing a description that actually triggers, and the provenance and privacy check before anything is committed.
---

# Write a Repo Skill

A skill is a working method an agent loads when it becomes relevant. This
repository keeps its skills **inside the repository** so that anyone who clones
it gets them, without needing the original author's machine.

Treat `AGENTS.md` at the repository root as authoritative if it and this skill
ever disagree.

## Is this actually a skill?

Write one when **all** of these hold:

- The method is **repeatable** — it applies to a class of situations, not one.
- It is **not obvious** — an agent gets it wrong or does it inconsistently
  without guidance.
- It is **stable** — it will still be right next month.
- It is **portable** — it does not depend on one person's machine, accounts, or
  private context.

Do not write one for:

- **A single decision.** That is `docs/decisions/`.
- **What happened in one experiment.** That is `knowledge/lessons-learned/`.
- **A reusable code fragment.** That is `knowledge/code-snippets/`.
- **A rule every agent must always follow.** That is `AGENTS.md` — skills load
  situationally; rules do not.
- **Something the agent already does well.** Instructions have a cost: they
  consume context and dilute the instructions that matter.

The honest test: *has this come up at least twice, and did the agent get it
wrong at least once?*

## Layout

```
.agents/skills/<skill-name>/
├── SKILL.md              # required — the skill itself
├── agents/
│   └── openai.yaml       # optional — display metadata for OpenAI-based agents
└── references/           # optional — detail loaded only when needed
    └── <topic>.md
```

Name the folder in `kebab-case`, and make the name describe the **job**, not the
topic: `debug-mantra` beats `debugging-notes`.

## Frontmatter

```markdown
---
name: <must match the folder name exactly>
description: <when to use this — see below>
---
```

**The description is the whole discovery mechanism.** An agent decides whether to
load the skill from this line alone, usually without reading the body. A
description that describes the *topic* will not trigger; one that describes the
*situation* will.

Weak:

```yaml
description: Best practices for debugging.
```

Strong:

```yaml
description: Find the actual cause of a bug instead of guessing at fixes. Use
  when something throws, returns the wrong value, works locally but not
  elsewhere, or when two or three attempted fixes have already failed.
```

Write it as **triggers**: the symptoms, the phrases a person would type, the
moments when it applies. Include the words someone would actually use, not the
words you would use to categorise it.

## Writing the body

- **Lead with the failure it prevents.** An agent reading it should know within
  two sentences why it exists.
- **Be concrete.** Commands, checklists, tables, before/after pairs. Prose about
  being careful changes nothing.
- **Give the order.** Cheapest and highest-yield checks first, so a partial read
  is still useful.
- **Include a "do not" section.** Named anti-patterns are more actionable than
  positive advice; they are recognisable in the moment.
- **Prefer short.** Every line competes for attention with every other line. If
  something is rarely needed, put it in `references/` and point at it.
- **Do not restate `AGENTS.md`.** Link to it and add a line saying it wins on
  conflict.

## Provenance and privacy — check before committing

This repository is shared. Anything committed here is readable by anyone who
clones it. Before adding or editing a skill:

- [ ] **No credentials.** No key, token, password, or connection string — not in
      examples, not in comments.
- [ ] **No personal paths.** No `C:\Users\<name>\…`, no `/home/<name>/…`.
- [ ] **No private context.** No customer names, internal URLs, business rules,
      pricing, or project specifics belonging to something outside this repo.
- [ ] **No copied third-party text.** Do not paste someone else's skill body.
      Write the method in your own words, or leave it out.
- [ ] **Examples are synthetic** and safe to share.
- [ ] **No machine dependency.** It must work after a plain `git clone`.

If a method is genuinely useful but its source is private or third-party,
**extract the smallest generalizable idea and write it fresh**. The idea is not
the property; the text is.

A quick sweep:

```bash
grep -rniE "C:\\\\Users|/home/[a-z]|sk-[A-Za-z0-9]|password|api[_-]?key" \
  .agents/skills/<skill-name>/
```

## Register it

A skill nobody can find does nothing. After creating one:

1. Add it to the skills list in `AGENTS.md`.
2. Add it to the structure tree and skills section in `README.md`.
3. Mention it in `CLAUDE.md` if Claude Code should know it exists.
4. Record a short decision in `docs/decisions/` — the repository requires this
   for a new skill or a change in a skill's scope.

## Then test it

Do not assume it works because it reads well.

- Start a fresh session and give it a realistic prompt that *should* trigger the
  skill. Did it load? If not, the description is the problem.
- Follow the skill yourself on a real task. Anything ambiguous in practice is
  ambiguous in the text.
- Check the frontmatter parses and `name` matches the folder.

## Maintaining it

- When a skill is wrong, fix it in the same session you noticed. A skill that
  has been wrong once is trusted less thereafter.
- When two skills start overlapping, merge them or sharpen the boundary — an
  agent choosing between near-duplicates chooses badly.
- Delete skills that stopped being true. A stale skill is worse than a missing
  one, because it is followed.
