---
name: local-dev-servers
description: Start, verify and hand off long-running local development servers when working with a coding agent. Use when an app needs a backend and a frontend running at once (FastAPI + React/Vite, Express + Next, Django + Vue, or similar), when a dev server will not stay running under an agent, when a localhost URL will not open or loads blank, when the agent reports a command timing out or being killed, or when deciding who should own the running process — the agent or the human.
---

# Local Dev Servers

Get a running app in front of the human, and keep it running. The obstacle is
rarely the application code — it is that a dev server never exits, and most
agent harnesses wait for commands to exit.

Treat `AGENTS.md` at the repository root as authoritative if it and this skill
ever disagree.

## The core constraint

A coding agent runs a command and waits for it to finish. `uvicorn`,
`npm run dev`, `next dev` and friends are designed never to finish. So a
foreground launch does one of three things: blocks the agent until it times
out, returns nothing useful, or gets killed during cleanup. The server was
usually fine. The way it was launched was not.

This produces a specific, misleading symptom: **the human is told the app is
running and the URL does not open.** Do not report a server as started on the
strength of having issued the command. Verify it, every time — see Verify below.

## Diagnose before changing anything

Three different failures look identical from the browser. Fixing the wrong one
wastes the session.

| Symptom | Likely failure | Confirm it |
|---|---|---|
| URL never loads; agent's command timed out or was killed | **Harness** — the process could not stay alive | Human runs the same commands in ordinary terminals. If the app works, it is this one |
| Server exits immediately with an error | **Dependencies** — packages missing, wrong virtualenv, unsupported runtime version | Read the actual error text; it names the cause |
| Page loads but is blank, or every API call fails | **Wiring** — dev-server proxy missing, wrong port, or CORS | Open the browser network tab; look for 404s or CORS errors on `/api/...` |

**The decisive test is free:** ask the human to run each command in its own
ordinary terminal, with no agent involved. Working there and failing under the
agent proves a harness problem and proves the project is sound. Do not start
editing configuration until you know which failure you have.

Common dependency errors and their real cause:

| Message | Cause |
|---|---|
| `Cannot find module 'vite'`, `vite is not recognized` | dependencies never installed in that folder |
| `ModuleNotFoundError: No module named 'fastapi'` | Python deps missing, or the virtualenv is not activated |
| `Unsupported engine`, `requires Node >= N` | runtime too old for the installed tooling |
| `EADDRINUSE`, `address already in use` | a previous run is still holding the port |

## Launch so the process survives

Prefer, in order:

**1. The human owns the servers.** The most reliable arrangement, and the one
to recommend by default: the human runs the servers in their own terminals; the
agent edits files. Agents are good at editing and bad at babysitting processes.
It also means a code change does not require the agent to restart anything.

**2. Spawn detached terminal windows.** When the agent should start things, have
it launch *windows* rather than host the processes. The spawn command returns
immediately, so nothing blocks, and the servers outlive whatever the agent does
next.

Windows (PowerShell):

```powershell
Start-Process powershell -ArgumentList "-NoExit","-Command","cd backend; <backend start command>"
Start-Process powershell -ArgumentList "-NoExit","-Command","cd frontend; npm run dev"
```

`-NoExit` keeps the window open if the server crashes, so the error stays
readable instead of vanishing with the window.

macOS / Linux:

```bash
nohup <backend start command> > backend.log 2>&1 &
nohup npm run dev > frontend.log 2>&1 &
```

Add the log files to `.gitignore`.

**3. The agent's own background mode.** If the harness has an explicit
background or detached option, use it — but tell the human the lifetime:
processes started this way normally die when the session ends. Say so before
they rely on it.

## Reduce the number of processes

Two servers is a development convenience, not a requirement. Fewer processes
means fewer things to keep alive.

**Build the frontend and serve it from the backend.** Compile the UI to static
files once, then let the backend serve them. One process, one port, no proxy,
no CORS. The cost is losing hot-reload — after a UI change the build must be
re-run.

```bash
npm run build     # emits static files, commonly into dist/ or build/
```

Mounting them depends on the backend framework; in FastAPI, for example:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="ui")
```

Mount the static handler **after** the API routes, or it will swallow them.

**Or run both under one supervisor.** Tools such as `concurrently` (Node) or a
`Procfile` runner start several servers from a single command. This helps when
the harness can hold one long-running process but not two. It does not help
when the harness cannot hold any — prefer detached windows there.

## Give the human one thing to run

A checked-in start script beats instructions. The human runs it once; the agent
never touches the servers.

```powershell
# dev.ps1 — start both servers and open the app
Start-Process powershell -ArgumentList "-NoExit","-Command","cd $PSScriptRoot\backend; <backend start command>"
Start-Process powershell -ArgumentList "-NoExit","-Command","cd $PSScriptRoot\frontend; npm run dev"
Start-Sleep -Seconds 3
Start-Process "http://localhost:<frontend port>"
```

Keep the ports in one place — a `.env` or a comment at the top of the script —
so the backend, the frontend proxy and this script cannot drift apart.

## Wire the frontend to the backend

In development the two servers are different origins, so the browser blocks
direct calls. Configure the dev server to proxy API paths to the backend rather
than loosening CORS. For Vite:

```js
// vite.config.js
export default {
  server: { proxy: { "/api": "http://localhost:<backend port>" } },
};
```

Then the frontend calls `/api/...` with no host, and the same code works
unchanged once the UI is built and served from the backend.

## Verify before saying it works

Never report a server as running because the command was issued. Check the
thing the human will actually do.

1. **Is the port listening?**
   - Windows: `Get-NetTCPConnection -LocalPort <port> -State Listen`
   - macOS / Linux: `lsof -i :<port>`
2. **Does the backend answer?** Request a known endpoint — a health route, or
   any route that returns quickly — and confirm the status code.
3. **Does the page load?** Fetch the frontend URL and confirm it returns HTML,
   not a connection error.
4. **Do the API calls work from the page?** The most-missed step. A page can
   load perfectly while every request fails. If a health route exists, call it
   through the frontend's origin so the proxy is exercised too.

Report what was checked and what came back. "Server started" is not evidence;
"port 5173 listening, `/api/health` returned 200" is.

## Hand off

Tell the human, in this order:

1. **The URL**, on its own line, ready to click.
2. **What is running** — which process on which port.
3. **How long it lives.** If the agent started it, say plainly whether it
   survives the session ending. This is the detail that most often surprises
   people.
4. **How to restart it themselves**, as a copyable command or the script name.

If a server had to be restarted mid-session to pick up a code change, say so —
otherwise a stale browser tab looks like a bug in the new code.

## Do not

- Do not add a frontend framework, bundler or build step to a project whose UI
  is already plain static files. Check what the project actually has first.
- Do not disable CORS globally to work around a missing dev proxy.
- Do not kill processes on a port without identifying them first; the port may
  belong to something the human is using.
- Do not claim an app works without loading it.
- Do not leave a background server running at the end of a session without
  telling the human it is there.
