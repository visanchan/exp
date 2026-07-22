# exp-004 — Weekday Bar Chart

## Experiment ID
`exp-004-weekday-bar-chart`

## Title
Create a PNG bar chart of weekday values.

## Date
Started: 2026-07-23
Completed: 2026-07-23

## Class topic
Basic data visualization.

## Objective
Turn five weekday values into a clear, shareable PNG bar chart.

## Hypothesis
A directly labeled vertical bar chart will make the relative size of the five values easy to compare at a glance.

## Success criteria
- [x] The PNG plots Mon 12, Tue 19, Wed 7, Thu 22, and Fri 15 accurately.
- [x] Every bar has a readable weekday label and value label.
- [x] The saved image opens correctly and is visually legible.

## Technology stack
| Component | Choice | Version | Why |
|---|---|---|---|
| Drawing | Windows System.Drawing | Installed .NET runtime | Creates the requested PNG without adding dependencies. |

Dependencies added beyond the standard library: none.

## Setup instructions
No setup is required to view the result — open
`artifacts/weekday-values-bar-chart.png` in any image viewer.

To regenerate it (Windows, uses the installed .NET runtime, no packages):

```powershell
powershell -ExecutionPolicy Bypass -File src/make-chart.ps1
```

## Implementation summary
A 1200×750 vertical bar chart rendered straight to PNG: one blue bar per
weekday, a fixed 0–25 value axis so gridlines land on round numbers, and a value
printed above each bar.

`src/make-chart.ps1` produces it. The first version of this experiment shipped
the PNG with no source, which made the artifact unreproducible and left this
README describing a tech stack nobody could run — the script was added
afterwards to close that gap.

## Test cases
| # | Case | Input / setup | Expected | Actual | Pass |
|---|---|---|---|---|---|
| 1 | Source values | Five supplied weekday values | All five values plotted exactly | Mon 12, Tue 19, Wed 7, Thu 22, Fri 15 are present | Yes |
| 2 | PNG structure | Generated artifact | Valid PNG with non-zero dimensions | 1200×750, 21,653 bytes | Yes |
| 3 | Visual inspection | Open final image | Labels and bars are legible | Opened at original resolution; title, axes, labels, and bars are clear | Yes |
| 4 | Reproducible from source | Run `src/make-chart.ps1` | Regenerates an equivalent 1200×750 chart | 1200×750, all five values and labels correct on visual inspection | Yes |

How tests were run:

```text
Read PNG header dimensions and SHA-256 hash with PowerShell, then open the PNG at original resolution for visual inspection.
```

## Results
All success criteria were met. The chart accurately presents the five supplied values and is ready to share as a PNG.

- Source accuracy — met; all five values and weekday labels were visually confirmed.
- File validity — met; PNG is 1200×750 and 21,653 bytes.
- Visual legibility — met; labels do not overlap and bar heights match the labeled values.

## Problems encountered
| Problem | Symptom | Root cause | Resolution |
|---|---|---|---|
| Artifact was not reproducible | PNG present, no source; README documented a stack with nothing to run | The chart was drawn inline and the code was never saved | Fixed — `src/make-chart.ps1` added and verified to regenerate the chart |
| Index row broke the table | `exp-004` row would not render on GitHub | Blank lines around the row, which terminate a Markdown table | Fixed in `archive/experiment-index.md` |
| Misleading log line in the script | Printed `1200 x 336` while writing a correct 1200×750 image | `$h` (bar height) shadowed `$H` (canvas height); PowerShell variables are case-insensitive | Fixed — renamed to `$barH`, with a comment so it is not reintroduced |

## Lessons learned
- Direct labels make a small one-series chart understandable without a legend.
- A built-in drawing library is sufficient for a simple static chart and avoids
  package setup.
- **An artifact without its source is a dead end.** The PNG was correct and
  verified, and still could not be changed, re-run at another size, or reused —
  the experiment folder is for the code that produces the artifact, not only the
  artifact.
- **Case-insensitive variable names bite quietly.** `$h` overwrote `$H` and the
  only symptom was a wrong number in a log line. Had that line been trusted, it
  would have looked like a real defect in the image.

## Security considerations
- Secrets used: none
- Secrets committed: **No**
- Sensitive or personal data handled: none
- Artifacts redacted before saving: n/a
- Third-party services data was sent to: none
- Residual risk / cleanup needed: none

## Cleanup decision
- Proposed: keep
- Reasoning: The PNG is the requested deliverable.
- Keep list: `src/make-chart.ps1`, `artifacts/weekday-values-bar-chart.png`,
  this README
- Delete list: none
- Approved by: pending — this experiment exists as a by-product of testing skill
  discovery, and is kept as the repository's only worked example of a completed
  experiment. Remove it whenever a real one takes its place.
- Executed on: n/a
- Checklist completed: no

## Final status
`Complete`

Index updated in `archive/experiment-index.md`: yes
