---
name: build-lab-meeting-slides
description: Build or revise polished, editable PowerPoint decks for research lab meetings from a supplied PPTX template, papers, code, transcripts, figures, and optional GPU measurements. Use for lab meetings, research talks, CUDA or systems presentations, and any request to preserve an existing PowerPoint visual style.
---

# Build Lab Meeting Slides

Make the presentation first. Preserve the user's visual source, tell one cumulative research story, and keep technical content editable.

Do not add workflow machinery that the user did not ask for. Style preferences are authoring guidance, not new schemas, reviewer forms, approval records, scorecards, or layers of tests. After the deck works, run one practical build check and inspect the rendered slides.

## Before editing

Read the complete Presentations skill and its template-following instructions. Use its PowerPoint runtime for imports, native edits, exports, rendering, and slide inspection. Read the PDF skill only when source PDFs need extraction or visual review.

Use this precedence:

1. the user's current request;
2. the supplied PPTX and source material;
3. the existing lab style;
4. generic presentation advice.

Never mix another deck's palette, branding, or decorative system into a supplied template unless the user asks.

## Default approach

When a PPTX template or existing deck is supplied:

- inspect its real slides;
- reuse proven source slides as frames;
- edit inherited title and text objects;
- place new editable research visuals in the existing body area;
- preserve masters, layouts, logos, rails, rules, type, spacing, and image crops;
- shorten or split copy when it does not fit;
- keep photographs, screenshots, and sourced figures as images;
- keep diagrams, arrows, arrays, tables, charts, and code callouts editable when practical.

If no template is supplied, use `assets/lab-meeting-template.pptx`. Its preview and hash are recorded in `assets/style-manifest.json`.

## Start a deck

Check the available tools:

```bash
python3 scripts/lab_slides.py doctor
```

Create a project:

```bash
python3 scripts/lab_slides.py init \
  --project-dir /absolute/path/to/project \
  --source-pptx /absolute/path/to/current-or-source-deck.pptx \
  --template-pptx /absolute/path/to/template.pptx \
  --output-name lab-meeting-final.pptx
```

Then:

1. State the audience outcome and central takeaway in `labdeck.json`.
2. Write the slide sequence in `content/slide-plan.json`.
3. Add only the claims and sources actually used in `content/claims.json`.
4. Write speaker notes in `content/notes.json`.
5. Run `prepare-template`.
6. Implement the deck-specific visuals in `build/builder.mjs`.
7. Run `audit`, `finalize`, and `qa`.
8. Open the final montage and fix visible problems.

```bash
python3 scripts/lab_slides.py prepare-template /absolute/path/to/labdeck.json
python3 scripts/lab_slides.py audit /absolute/path/to/labdeck.json
python3 scripts/lab_slides.py finalize /absolute/path/to/labdeck.json
python3 scripts/lab_slides.py qa /absolute/path/to/labdeck.json
```

Read [workflow.md](references/workflow.md) for the project sequence and [template-native.md](references/template-native.md) for source-slide mapping.

## Story and slide planning

Write one sentence before layout:

> By the end, this audience should understand or decide X because Y.

Every slide gets:

- one narrative job;
- one audience-facing title claim;
- one suitable source frame;
- the evidence it actually uses;
- a visual anchor when a diagram, chart, code delta, or figure explains the point better than prose;
- notes that explain the slide and transition.

A minimal content entry looks like:

```json
{
  "slide": 2,
  "narrative_job": "mechanism explanation",
  "title_claim": "Coalesced access removes redundant memory transactions",
  "template_frame": {
    "role": "content",
    "source_slide": 2,
    "routing_rationale": "The source content frame provides the needed title and body area."
  },
  "visual_anchor": "lanes, addresses, and the changed transaction count",
  "coverage": ["memory coalescing"],
  "evidence_refs": ["k2-time", "k2-sectors"],
  "notes_ref": "slide-02"
}
```

For an incremental code story, keep unchanged coordinates stable, show the exact changed line, and pair the change with its mechanism and measured consequence.

## Visual direction

Favor one meaningful composition over a grid of generic interface components. Avoid decorative pills, dashboards, repeated icon blurbs, fake navigation, filler copy, arbitrary gradients, and shadows that do not explain anything.

Use clear technical visuals: flows, timelines, arrays, memory paths, before/after code, tables, and charts. Create connectors before nodes. Keep normal body text at least 16 pt unless the supplied template clearly supports another readable size. Inspect Korean and CJK line breaks in full-size renders.

`assets/template-builder-scaffold.mjs` imports the prepared starter, edits mapped objects, adds native text, shapes, and lines in the content area, and exports the deck. Extend it directly for the visuals the research needs.

## Motion

Use motion only when state change, scheduling, transfer, or interaction is materially easier to understand over time. A static slide is the default.

Two optional Manim starters are included:

```bash
python3 scripts/motion_assets.py doctor
python3 scripts/motion_assets.py render \
  --project /absolute/path/to/project \
  --preset serving \
  --output assets/motion/serving.gif \
  --palette assets/style-manifest.json
```

Available presets are `serving` and `syscall`. Custom scenes can use `--source` and `--scene`. The command also writes a poster PNG for static review. See [motion-and-domain-visuals.md](references/motion-and-domain-visuals.md).

## Evidence and measurements

Measurements are opt-in. Read [measurement-policy.md](references/measurement-policy.md) before running a benchmark.

- Use `lab_slides.py gpu` only when the user requests live GPU evidence.
- Keep timing, profiler attribution, and system timelines distinct.
- Label measured, derived, vendor, and inferred claims accurately.
- Never use profiler replay time as application timing.
- Do not imply causality beyond the evidence.

## Speaker notes

Replace sample template notes unless the user explicitly wants them preserved.

Useful ranges:

- cover, divider, and closing: 20–100 words;
- mechanism and evidence: 90–190 words;
- appendix and references: 40–120 words;
- ordinary content: 60–170 words.

These are editing defaults, not padding targets. Explain purpose, mechanism, numerical meaning, provenance, caveat, and transition only when relevant.

## Final review

`qa` checks the package, notes, rendered slides, basic overflow, and template preservation. It writes a review montage. Inspect that montage for hierarchy, clipping, line breaks, visual repetition, misleading emphasis, and whether each slide communicates its point quickly.

Fix visible issues in the deck itself. Do not create extra review documents unless the user requests them.

Deliver the final editable PPTX and a concise note about sources, measurement scope, and any unresolved limitation.

## Included files

- `assets/lab-meeting-template.pptx`: default editable template.
- `assets/lab-meeting-template-preview.png`: template preview.
- `assets/style-manifest.json`: template identity and practical style defaults.
- `assets/template-builder-scaffold.mjs`: starter import/edit/export implementation.
- `scripts/lab_slides.py`: project, build, and review commands.
- `scripts/motion_assets.py`: optional Manim rendering helper.
