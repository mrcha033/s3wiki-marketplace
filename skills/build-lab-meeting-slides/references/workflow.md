# Workflow

Use the smallest sequence that produces a good editable deck.

## 1. Inspect the inputs

- Read the user brief and source material.
- Open the supplied PPTX and inspect real slides, not just layout names.
- Identify reusable cover, section, content, comparison, evidence, and closing frames.
- Note the existing palette, typography, title placement, body area, logos, and recurring spacing.

If no template is supplied, use the bundled lab template.

## 2. Decide the story

Write the audience outcome and central takeaway in one sentence. Build a short sequence where every slide advances that argument.

For each slide, record:

- narrative job;
- title claim;
- source frame;
- evidence references;
- visual anchor;
- speaker-note reference.

Do not create fields that the deck does not need.

## 3. Prepare the starter

Run:

```bash
python3 scripts/lab_slides.py prepare-template /absolute/path/to/labdeck.json
```

This maps the plan to source slides and creates a starter PPTX. If the title does not fit its inherited box, shorten it or choose a better frame.

## 4. Build the content

Edit `build/builder.mjs`.

- Keep inherited template objects in place.
- Rewrite mapped title and subtitle objects.
- Add editable diagrams, tables, charts, code, and labels inside the content area.
- Use images for photographs, screenshots, and sourced figures.
- Keep repeated-slide geometry stable when the story depends on comparison.
- Use motion only when state change is the lesson.

Build the main explanation first. Add detail only when it helps the audience.

## 5. Add notes

Write notes for the actual slide role. Replace sample notes from the template. Avoid padding, invented interpretation, and repetition of visible text.

## 6. Build and inspect

```bash
python3 scripts/lab_slides.py audit /absolute/path/to/labdeck.json
python3 scripts/lab_slides.py finalize /absolute/path/to/labdeck.json
python3 scripts/lab_slides.py qa /absolute/path/to/labdeck.json
```

Open the montage produced by `qa`. Check:

- title and body fit;
- readable type;
- Korean and CJK wrapping;
- clear hierarchy;
- accurate figures and labels;
- no accidental object overlap;
- no template drift;
- one clear takeaway per slide.

Fix the deck and rerun `finalize` and `qa` after material edits.

## 7. Deliver

Return:

- the editable final PPTX;
- a short description of the narrative;
- sources or measurement scope when relevant;
- any limitation that remains visible or factual.

Do not add reviewer forms, approval logs, or extra process documents unless the user asks for them.
