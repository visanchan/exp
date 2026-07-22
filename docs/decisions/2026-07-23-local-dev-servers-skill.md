# Second Repo-Local Skill: Local Dev Servers

## Context

A classmate working on a two-process app (Python backend + React/Vite frontend)
could not get the app to open in a browser while working through a coding agent.
The agent reported a dependency problem. Running the same two commands manually,
in two ordinary terminals, worked immediately.

The cause was not dependencies and not the project. A dev server never exits,
and agent harnesses generally run a command and wait for it to exit — so a
foreground launch blocks until timeout or is killed during cleanup. The reported
error pointed at the wrong layer, and the time went into chasing it.

This is not specific to one person or one stack. Any student running a
backend-plus-frontend project through an agent will hit it, the symptom
("the URL doesn't open") is identical across three unrelated causes, and the
cheapest diagnostic — run it manually in two terminals — is not obvious.

The first repo-local skill, `ai-class-operating-partner`, covers experiment
workflow and deliberately does not cover process lifecycle.

## Decision

Add a second repository-local skill at `.agents/skills/local-dev-servers/`.

Scope: diagnosing which of the three failures is in play, launch patterns that
survive an agent session, reducing two processes to one, dev-server-to-backend
wiring, verification before claiming success, and handing the URL to a human
with its real lifetime stated.

It carries the repository's evidence rule into a place where it is routinely
broken: a server may not be reported as running because the command was issued.
Only a listening port, an answered request and a loaded page count.

Constraints applied, per `docs/decisions/2026-07-22-portable-repo-local-class-skill.md`:

- Depends only on files committed in this repository.
- No credentials, personal paths, machine specifics, or private project context.
- Framework-agnostic; commands are shown as placeholders rather than one
  project's exact invocation.
- `AGENTS.md` remains authoritative.

An `agents/openai.yaml` interface file is included, matching the existing skill's
layout, because the immediate audience uses an OpenAI-based agent.

## Consequences

- Anyone cloning this repository gets the diagnostic and the fix without needing
  the owner's machine or setup.
- The repository now has two skills. Future additions should stay similarly
  narrow rather than growing either skill into a catch-all.
- The skill states that agent-started servers usually die with the session.
  That is a property of current harnesses, not a law; if that changes, the
  hand-off section needs revisiting.
- The guidance is drawn from observed behaviour across a small number of
  harnesses. Specific commands are Windows-first with macOS/Linux equivalents,
  reflecting where it was tested; other environments may need adjustment.
