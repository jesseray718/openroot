# Claim Status Standard

OpenRoot separates ideas, documentation, and demonstrated results. This makes
the work easier to evaluate, reproduce, improve, and safely build upon.

## Status Labels

| Status | Meaning | Minimum public support |
|---|---|---|
| `demonstrated` | A result has been produced and can be checked. | Method, artifact or measurement, conditions, and limitations. |
| `documented` | A source, record, or external result is described. | Citation or provenance plus a clear statement of what has not been independently reproduced. |
| `proposed` | A design, plan, hypothesis, or intended experiment. | Purpose, assumptions, expected test, and failure criteria where applicable. |
| `speculative` | An exploratory interpretation or untested possibility. | Clear uncertainty label and no presentation as established fact. |

## Applying Labels

Use the narrowest defensible label. A design can be `demonstrated` in one
respect and `proposed` in another. For example, a sensor enclosure may be
built and measured while its long-duration performance remains proposed.

Do not upgrade status based only on plausibility, simulation, narrative,
or a tool-generated summary.

## Evidence Links

A substantive `demonstrated` claim should identify:

- The relevant design or claim identifier.
- A measurement method, procedure, or test plan.
- Inputs, conditions, and constraints.
- Observed output, artifact, or result.
- Known limitations and open questions.

## Safety and Scope

A claim label is not a safety certification, regulatory approval, warranty,
or fitness-for-purpose statement. Hardware, energy, thermal, material, and
field-work documents must state applicable safety constraints separately.

## Review

Contributors should retain the existing status when evidence is incomplete.
A status change should explain what new publicly reviewable evidence supports
the update.
