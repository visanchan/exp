# Output Standards

Read the section that matches the requested deliverable.

## Every task

- Start with the intended outcome.
- Use plain professional language and explain necessary jargon.
- Prefer a useful small result over an impressive large system.
- State important assumptions.
- Preserve existing behavior and user-authored work.
- Finish with test evidence, risks or limitations, and the recommended next action.

## Business recommendation

Connect the recommendation to:

1. Business objective.
2. Expected benefit.
3. Implementation difficulty.
4. Cost and complexity tradeoff.
5. Next action.

When tradeoffs matter, compare a quick fix, a balanced option, and a scalable option. Do not create artificial options when one route is clearly sufficient.

## Data analysis

- Describe the dataset before drawing conclusions.
- Identify missing data, inconsistent formats, and decision risks.
- Label observations separately from recommendations.
- Prioritize actions as high, medium, or low.
- Quantify business impact where the evidence permits it.
- Never imply causation from correlation without support.

## Code or automation

- Keep architecture simple and names readable.
- Avoid unnecessary dependencies and abstraction.
- Validate important inputs and handle consequential failures.
- Include a clear run command.
- Test the normal path plus a meaningful edge or failure case.
- Report exact test outcomes; disclose skipped checks.

## Internal tool or UI

- Optimize common staff tasks for speed and clarity.
- Use readable hierarchy and obvious actions.
- Reduce repeated entry through safe defaults or auto-fill.
- Validate consequential fields and preserve final human review.
- Make exports, printing, or sharing straightforward when relevant.
- Verify keyboard use, focus, labels, contrast, errors, and responsive behavior.

## Spreadsheet

- Separate raw inputs, mappings or assumptions, calculations, and final outputs.
- Use clear headers, stable identifiers, consistent types, and explicit units.
- Avoid hidden constants in formulas.
- Add data validation where it prevents expensive mistakes.
- Verify formulas, totals, filters, freeze panes, and exported values.
- Keep compatibility with normal Excel workflows unless a stronger requirement exists.

## Document, PDF, or presentation

- Structure the message before styling it.
- Keep claims defensible and evidence close to the claim.
- Render and inspect the final artifact when layout matters.
- Use visuals only when they clarify a relationship or decision.
- Make the artifact understandable without the surrounding chat.

## Final handoff

Report:

1. Outcome and business or learning value.
2. Files created or changed.
3. How to run, open, or use the result.
4. Tests performed and actual results.
5. Risks, assumptions, or remaining decisions.
6. Best next improvement.
