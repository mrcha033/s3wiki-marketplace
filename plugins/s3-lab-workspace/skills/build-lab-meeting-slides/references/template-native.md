# Editing a supplied PPTX

The rendered source slides are the visual source of truth.

## Reuse proven frames

Inspect every source slide and select the frames that already work for the needed roles. Duplicate those slides when preparing the starter. Do not assume an unused layout name will render like an approved slide.

The generated frame map records:

- output slide number;
- source slide number;
- narrative role;
- inherited objects that may be rewritten;
- the content area for new editable objects.

## Preserve the template

Keep inherited masters, layouts, theme references, logos, rails, rules, title geometry, paragraph spacing, and image crops unless the user asks for a change.

When copy does not fit:

1. shorten it;
2. split the idea;
3. select a better source frame.

Do not cover the source slide with a second full-slide design.

## Add research content

The starter builder supports native text, shapes, and lines. Extend it for charts, tables, diagrams, arrays, code, and other research-specific visuals.

- Create connectors before nodes.
- Keep normal body text readable.
- Keep new objects inside the body area.
- Use source images only when the content is naturally raster.
- Prefer editable primitives for explanatory diagrams.

## Practical checks

`prepare-template` checks the mapping and creates the starter. `audit` checks the current plan and file references. `finalize` builds the deck and attaches notes. `qa` renders the final PPTX, looks for overflow, and checks that inherited template content was not unexpectedly changed.

These checks catch mechanical problems. The montage remains the best way to judge hierarchy, spacing, repetition, and audience readability.
