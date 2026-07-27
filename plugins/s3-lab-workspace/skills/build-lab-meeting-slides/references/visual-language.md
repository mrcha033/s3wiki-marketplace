# Visual-language contract

## Contents

- Precedence
- English and title rules
- Closed color system
- Figure-first composition
- No-filler rule
- Typography and editability
- Incremental and hardware figures
- Design precedents
- HTML boundary

## Precedence

Treat the user-designated PPTX as the structural and brand contract. If no newer
template is supplied, use `assets/lab-meeting-template.pptx` and verify its hash
against `assets/style-manifest.json`.

Apply this order:

1. explicit user brief;
2. inherited source objects and measured layout evidence;
3. approved content and evidence;
4. closed copy, palette, and figure contracts;
5. generic design guidance.

Do not introduce a second template or visual reference. Preserve masters,
layouts, title geometry, logos, rails, rules, and source-authentic institutional
marks. Generated body content remains subject to the stricter rules below.

## English and title rules

- Write all generated visible copy and speaker notes in English.
- Preserve non-English text only inside locked inherited institutional marks,
  exact citations, code literals, or equations.
- Translate or replace non-English labels embedded in figures before delivery.
- Keep the schema key `title_claim`, but write a 1–3 word keyword/noun phrase.
- Keep titles on one line, normally within 42 characters.
- Do not use terminal punctuation, clauses, pronouns, or sentence headlines.
- Keep the full claim in the figure, evidence relationship, or narration.

Examples:

| Use | Reject |
|---|---|
| `Memory Coalescing` | `Coalesced access removes redundant transactions` |
| `Ablation Effects` | `The ablation shows that caching matters` |
| `Failure Modes` | `Why the current kernel still fails` |
| `Next Experiments` | `We will test three alternatives next` |

## Closed color system

Record the full source theme only as provenance. Generated objects may use only
the semantic tokens in `style.active_palette`.

For the retained Yonsei S3 template:

| Token | Value | Use |
|---|---|---|
| `background` | `#FFFFFF` | slide canvas |
| `surface` | `#FFFFFF` | unfilled or white figure surfaces |
| `ink` | `#001233` | primary text and dark structure |
| `muted` | `#5C677D` | secondary labels and sources |
| `primary` | `#0353A4` | connectors, axes, and main data series |
| `focus` | `#2269FE` | one declared focal change or result |
| `soft` | `#D2E1FE` | restrained grouping or comparison fill |

Use token names in `slide-plan.json`; never enter raw hex values. Keep white and
ink dominant. Use `primary` for stable structure and `focus` for one declared
target. Do not rotate accent colors by section, use rainbow scales, gradients,
shadows, decorative red strokes, or color without a semantic reason. Repeat the
same concept in the same color throughout the deck. Encode critical distinctions
with labels, position, or line style as well as color.

## Figure-first composition

Give every body slide one primary figure, plot, table, comparison, image, code
delta, or mechanism diagram. Target 60–75% of the approved body zone; the
automated floor is a 50% bounding span. Text-only slides, large prose boxes, and
decorative rectangles do not satisfy the figure gate. Information-bearing
visual-role geometry must also occupy at least 18% of the body zone, preventing
widely separated tiny marks from faking a dominant figure.

For `process`, `mechanism`, `flow`, `pipeline`, `architecture`, and `system`
anchors built from native primitives, use at least two meaningful
`diagram-node` objects joined by a `connector`, plus at least two concise
figure labels. A sourced image, data-backed plot, data-backed table, or editable
code view is an alternate figure and does not need synthetic nodes. Role labels
alone never prove structure: a rectangle tagged `plot` is still a rectangle.
Primitive plots need two axes and at least two data marks; image/table/chart
objects need an explicit source or data reference.

Use this order:

1. select the one message and evidence;
2. choose the figure family that reveals it;
3. establish reading order and stable coordinates;
4. add direct labels, axes, units, and up to three brief callouts;
5. remove prose, duplicate legends, ornamental icons, and unexplained color.

For paper figures, do not paste a dense multi-panel manuscript figure unchanged.
Select the relevant panel or rebuild the comparison, enlarge labels and axes,
remove irrelevant series and gridlines, and preserve source provenance. Results
normally use one plot or panel per slide. Methods normally use one pipeline,
architecture, or mechanism diagram. Comparisons use a direct two-state or
before/after composition with stable coordinates.

Give each text-bearing native element a `text_role`:
`figure-label`, `axis-label`, `legend`, `callout`, `annotation`, `source`,
`metadata`, `code`, `table`, or `equation`.

Give each non-text native element a `visual_role`:
`diagram-node`, `connector`, `data-mark`, `axis`, `plot`, `table`, `code`,
`image`, `annotation`, or `boundary`.

Treat those roles as audited declarations. Boundary and annotation rectangles
do not contribute to information-bearing figure area. Primitive plots require
orthogonal line axes and at least two numeric or source-bound data marks.
Chart/plot objects require numeric series/data or a bound source reference;
string-only labels do not establish plotted evidence.

## No-filler rule

Visible words exist only to read the figure or provide required metadata.
Do not add:

- decorative subtitles, straplines, slogans, or transition prose;
- repeated takeaway sentences below a figure;
- internal workflow terms, prompt text, preset names, or production notes;
- placeholders such as TODO, TBD, sample text, or click-to-add prompts;
- invented captions, claims, numbers, people, quotes, or evidence.

Keep ordinary body slides within 45 generated visible words. Keep each callout
within 12 words and use no more than three. Put explanation, interpretation,
transitions, caveats, and provenance detail in English speaker notes.
Body-frame rewrites are title-only by default. Do not smuggle visible prose
through arbitrary `content` fields; use role-tagged native elements for concise
figure copy and provenance.

## Typography and editability

Preserve inherited typography, spacing, insets, alignment, and title geometry.
Use Courier New for editable code only when the source has no code style.
Keep technical labels at least 16 pt. Shorten, restructure, or split instead of
shrinking. Audit direct object fonts and theme references.

Use native editable objects for arrays, matrices, lanes, addresses, memory
paths, arrows, synchronization boundaries, code deltas, tables, charts, and
simple conceptual hardware maps. Create connectors before nodes. Use authentic
raster assets for photographs, screenshots, sourced figures, and approved
illustration. A slide-sized raster wrapper is a Critical native-mode defect.
Use a native `rightArrow` shape when the shipped scaffold needs a simple
directional link; do not rely on unverified arrowhead metadata on a free line.

## Incremental and hardware figures

Keep unchanged objects at identical coordinates across incremental slides.
Ghost the previous state and highlight only the changed code line, lane mapping,
address, synchronization, grid geometry, or measured result.

Label conceptual hardware diagrams `conceptual — not to scale`. Distinguish
memory hierarchy, scheduler/warp state, allocation limits, architectural maxima,
and measured device attributes. Do not imply undocumented physical pipelines or
invent die-level detail.

## Design precedents

This contract adapts transferable patterns from:

- Anthropic's public PPTX skill: dominant palette, repeated motif, visual on
  every slide, placeholder search, and full-deck render review:
  <https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md>
- Microsoft PowerPoint guidance: minimal text, consistent backgrounds, clear
  graphics, and deck-wide color coherence:
  <https://support.microsoft.com/en-us/powerpoint/tips-for-creating-and-delivering-an-effective-presentation>
- MIT AeroAstro Communication Lab: one message per slide, succinct titles, and
  presentation-specific figure simplification:
  <https://mitcommlab.mit.edu/aeroastro/commkit/slide-design/>
- PLOS Computational Biology: visualization-led slides, short text fragments,
  and splitting dense manuscript figures:
  <https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1009554>
- Nature Research Figure Guide: efficient panels, high contrast, restrained
  palettes, and avoidance of rainbow/red-green encodings:
  <https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/>

The user-specific keyword-title rule overrides sources that prefer
assertion/sentence headlines.

## HTML boundary

An HTML prototype must use the inspected canvas, body zone, active palette,
English copy contract, and figure grammar. Reconstruct the accepted composition
in the native starter PPTX. Direct conversion or rasterization does not inherit
the original master/layout contract and remains a partial fallback.
