---
name: requirements-workbook
description: Before building something, generate a plain-language HTML workbook that asks the person what they actually want, then open it for them. They answer multiple-choice questions written in business language, add comments, click one button to copy everything, and paste it back. Use when a build request is ambiguous, when requirements live in someone's head, when the person is not technical, when you are about to guess at a decision that would be expensive to reverse, or when the request is a one-liner for something that needs a dozen decisions.
---

# Requirements Workbook

The expensive failure is not bad code. It is well-built code that answers the
wrong question, discovered after it is finished — because the agent guessed at a
dozen decisions rather than asking about the two or three that mattered.

Asking in chat has its own problem: a wall of questions is exhausting, easy to
answer vaguely, and the answers scatter across a conversation. A workbook fixes
both. One artifact, answered at the person's pace, returned as a single block of
structured text.

Treat `AGENTS.md` at the repository root as authoritative if it and this skill
ever disagree.

## When to build one

- The request is short and the build is not. *"Make me a tool that tracks
  orders"* hides a dozen decisions.
- The requirements exist only in someone's head, and they are the only source.
- The person is not technical, so chat questions in engineering vocabulary will
  get shrugs or guesses.
- A wrong guess would be costly to unwind — data model, scope, who can see what.

**Do not build one** for a small, well-specified change, when you can read the
answer from the code, or when you only have one real question. Ask that one
question. A workbook for a two-minute task is friction wearing a form.

## The one rule for choosing questions

**Ask only what changes what you build.**

For every candidate question: *if they answer A instead of B, do I write
different code?* If not, cut it. Curiosity is not a requirement.

Aim for **5–12 questions**. Beyond that, completion rates fall and answers get
careless — you will get worse information from more questions.

Rank them so that if the person stops halfway, you still have the decisive ones.

## Write in their language, not yours

Every question is a decision translated out of engineering vocabulary. Never ask
about the mechanism; ask about the outcome they care about.

| Instead of | Ask |
|---|---|
| Do you need authentication? | Should people have to log in, or can anyone with the link use it? |
| Should data persist? | If you close this and come back tomorrow, should your information still be here? |
| Do you need a database or is a file fine? | Will one person use this, or several people at the same time? |
| Should it be responsive? | Will you use this on your phone, or only on a computer? |
| Do you want API integration? | Should it fetch the numbers automatically, or will you paste them in? |
| What is the deployment target? | Does anyone else need to open this from their own computer? |
| How should errors be handled? | If something goes wrong, should it stop and tell you, or keep going quietly? |
| What is the MVP scope? | If only one thing worked by Friday, which one would it be? |
| Do you need role-based access? | Should everyone see everything, or should some people see less? |

**Give every option its consequence.** A non-technical person cannot choose
between options they cannot price:

```
Where should the information live?

( ) Only on my computer          — simplest; nobody else can see it
( ) A file I can send to people  — you email or share it manually
( ) Online, always available     — anyone with the link, but takes longer to build
```

That is a decision someone can actually make. "SQLite, JSON, or Postgres?" is not.

Mark the option you would pick as **(recommended)** and say why in a few words.
Most people want a default they can override, not a blank slate.

## What the workbook must do

Generate **one self-contained `.html` file** — no CDN links, no external fonts,
no build step. It has to work by double-clicking it, offline, on a machine with
nothing installed.

Required:

1. **A short intro** — what is being built, why the questions exist, how long it
   takes ("about 5 minutes").
2. **Questions grouped in sections**, each with a plain-language heading.
3. **Radio buttons or checkboxes**, every option carrying its consequence, plus
   an **"Other"** free-text box on any question where the options might not fit.
4. **A comment box per section** — "anything else about this?" The most useful
   answers usually arrive here, in the person's own words.
5. **One "Copy my answers" button** that puts everything on the clipboard as
   structured text, with visible confirmation that it worked.
6. **Unanswered questions listed explicitly** in the copied output, so you can
   tell "no" from "didn't get to it" — the difference matters and is invisible
   otherwise.

A complete, working template is in
[`references/workbook-template.html`](references/workbook-template.html). Copy it
and replace the questions; do not rebuild the clipboard logic from scratch.

## Delivering it

1. Write the file somewhere obvious — their Desktop or the project folder — with
   a name that says what it is: `order-tracker-questions.html`.
2. **Open it for them.** Do not leave a path in chat for them to find.
   - Windows: `Start-Process <path>`
   - macOS: `open <path>`
   - Linux: `xdg-open <path>`
3. Tell them in one line: answer what you can, skip what you are unsure about,
   click the button at the bottom, paste it back here.
4. **Stop and wait.** Do not start building against assumptions while they
   answer — that is the failure the workbook exists to prevent.

## Reading the answers back

When they paste, before writing any code:

- **Reflect the decisions back** in two or three sentences, in their language.
  This is the last cheap moment to catch a misunderstanding.
- **Name what is still open**, including anything they skipped, and say what you
  will assume for each. State the assumption rather than silently picking.
- **Flag any answer that surprises you.** An unexpected answer is often a
  misread question, and it is far cheaper to re-ask now.
- Then build.

Keep the pasted answers in the project — a `notes/` file or the experiment
README. They are the requirements record, and in three weeks nobody will
remember why a decision went the way it did.

## Do not

- Do not ask questions whose answers would not change the build.
- Do not use engineering vocabulary in a workbook for a non-technical person.
- Do not offer options without their consequences — that is a quiz, not a
  decision.
- Do not exceed ~12 questions. Split into a second round if you truly need more.
- Do not depend on a CDN, a font service, or an internet connection.
- Do not start building while they are still answering.
- Do not treat a skipped question as a "no".
