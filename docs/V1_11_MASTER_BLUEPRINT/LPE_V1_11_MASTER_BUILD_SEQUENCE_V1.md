# LPE V1.11 Master Build Sequence V1

## Current rule
This document is design-only. Do not commit/push/deploy feature code until local gates pass.

## Phase order

### Phase 0 — Stabilize Current State
- Check git status.
- Preserve current app.py backup.
- Mark previous Step 1C long-form patch as HOLD unless accepted later.
- Repair runtime-only blockers in a separate narrow hotfix if needed.
- No push/deploy.

### Phase 1 — Master Blueprint and Schema
- Install master blueprint.
- Create 5-mode Core Life Profile schema.
- Create acceptance criteria.
- No app.py mutation.

### Phase 2 — Settings: 5-Mode Life Story
- Replace setting experience with 5 story modes.
- Each mode must include: story input, guided prompts, system understanding summary, “used for” explanation.
- No daily plan engine yet.

### Phase 3 — Daily Check-in
- Add today context.
- Capture sleep, energy, shift, urgent events, today story, constraints.
- Must not overwrite core life profile.

### Phase 4 — Daily Plan Engine V2
- Use profile + daily context + learned patterns.
- Create timetable with reasons and fallback.

### Phase 5 — Task Result + Reflection
- Capture done/partial/skipped, actual minutes, difficulty, energy after, notes.
- Summarize what worked and what failed.

### Phase 6 — Learned Patterns
- Detect repeated patterns after enough evidence.
- Suggest profile updates only after user approval.

### Phase 7 — Persistence V1
- Export/import JSON first.
- Keep login/database for later.

### Phase 8 — Local UX Verification
- Compile.
- Run local.
- Verify mobile readability and navigation.
- Verify setting/check-in/plan/reflection flows.

### Phase 9 — Commit / Push / Deploy
- Commit only after local PASS.
- Push.
- Wait deployment.
- Public verify.

## Non-negotiable gates
- No app.py mutation in design-only gates.
- No deploy while local app is broken.
- No generic plan output.
- No profile overwrite from one-day reflection.
