---
name: build-lab-meeting-slides
description: Build or revise polished, editable PowerPoint lab-meeting decks from a supplied PPTX template, research sources, code, transcripts, and optional GPU evidence. Use whenever the user asks for a lab meeting, research talk, CUDA/performance deck, or says to preserve a lab/corporate PPTX template. The skill defaults to exact source-slide cloning, native editable objects, detailed template fidelity QA, audience-first narrative, and role-aware speaker notes; it can use HTML only as an optional visual prototype, never as an unmarked fidelity shortcut.
---

# Build Lab Meeting Slides

Build a strong research story inside the user's actual PowerPoint system. Make the deck visually quiet, technically precise, and figure-led.

## Non-negotiable output contract

Apply these rules to every generated deck. They are pinned by the skill and cannot be weakened from project configuration:

- Write all generated visible copy and speaker notes in English. Preserve non-English text only when it is locked inside an inherited logo, institutional mark, citation, code literal, or equation.
- Use keyword titles, not sentence headlines. The schema key remains `title_claim` for compatibility, but its value must be a one-line 1–3 word English noun/keyword phrase, normally no more than 42 characters, with no terminal punctuation or clause markers. Prefer `Memory Coalescing`, `Ablation Effects`, or `Next Experiments`; reject `Coalesced access removes redundant transactions`.
- Add no filler. Do not invent subtitles, straplines, transition prose, summaries, slogans, decorative captions, or internal process text. Keep explanations in speaker notes. Visible text is limited to required metadata, figure labels, axes, legends, concise annotations, evidence callouts, code deltas, and sources. When the retained cover maps a subtitle/date-presenter field, fill it only with compact required metadata.
- Make one content-specific figure, plot, table, image, comparison, or mechanism diagram the primary read on every body slide. Target 60–75% of the body zone; the automated minimum figure-span gate is 50%. A text box or large decorative rectangle is not a figure.
- Use the closed semantic palette declared in `style.active_palette`. For the retained template, use only `background`, `surface`, `ink`, `muted`, `primary`, `focus`, and `soft`. Never enter raw hex colors in slide-plan additions, rotate colors by section, add gradients/shadows, or use more than one focus treatment on a slide.
- Give every text-bearing native element a `text_role` and every non-text element a `visual_role`. Use these roles to prove that each object carries information rather than decoration.

These requirements intentionally override generic presentation advice that prefers full-sentence takeaway headlines. Preserve the one-message-per-slide principle, but express that message through the figure and spoken narration rather than a sentence title.

## Required companion skills

Before inspecting or editing a deck, read the complete `Presentations:Presentations` skill, its content rules, and its template-following reference. Its Artifact Tool runtime and exact clone/edit helpers are the implementation source of truth. Read the PDF skill when PDFs must be extracted or visually inspected.

Use these ideas from the named companion skills:

- `slides-grab`: Plan → Design → Export order, style approval, fresh render evidence, and two independent design reviews.
- `frontend-design`: a subject-specific visual thesis, a compact token system, one justified signature, no filler copy, and self-critique against generic defaults.
- `template-creator`: retain the original Office file and a verified preview as hash-pinned visual provenance.
- Canva branded presentations: separate the approved visual direction from the final editable candidate. A supplied template already establishes the direction; do not invent competing candidates.

## Route before authoring

Choose one authoring mode. The first match wins.

1. `template-native` — default whenever the user supplies a PPTX, asks to preserve a template, or edits an existing deck. Duplicate mapped source slides and edit inherited objects.
2. `native-original` — only when no user visual source exists. Declare and approve a design system before authoring.
3. `html-assisted-native` — optional when the user requests browser-based iteration or it materially improves composition review. HTML is disposable; the approved composition is rebuilt in the native starter PPTX.
4. `raster-fallback` — only after native editing is proven blocked and the user explicitly accepts reduced editability.

Precedence is: explicit user brief → user template and inherited source objects → approved content/evidence → the closed body-palette and copy contracts → generic design defaults. Do not mix in a second visual reference.

## Default retained template

`assets/lab-meeting-template.pptx` is the default S3/Yonsei template retained from the user's source file; `assets/lab-meeting-template-preview.png` is its inspected cover preview. Its expected SHA-256 is recorded in `assets/style-manifest.json`.

The template has two proven source frames:

- source slide 1: cover;
- source slide 2: content shell with inherited title and a bounded body zone.

Clone slide 1 once for the opening. Clone slide 2 for body slides. Do not create slides from the template's unused layout names: an available layout is not a proven rendered frame.

## Start here

Run the environment check:

```bash
python3 scripts/lab_slides.py doctor
```

Initialize one project per deck. `--template-pptx` may point to a newer user template; otherwise the retained S3/Yonsei template is used.

```bash
python3 scripts/lab_slides.py init \
  --project-dir /absolute/path/to/project \
  --source-pptx /absolute/path/to/content-or-current-deck.pptx \
  --template-pptx /absolute/path/to/template.pptx \
  --output-name lab-meeting-final.pptx
```

`init` inspects every template slide, writes a hash-pinned profile and design declaration, and copies a native builder scaffold. Then:

1. Fill `deck.communication_job` in `labdeck.json` using: “By the end, [audience] should [outcome] because [central takeaway].”
2. Fill `content/outline.md`, `content/slide-plan.json`, `content/claims.json`, and `content/notes.json`.
3. Review `content/design-system.json`. Keep the full source theme as provenance, but use only the closed semantic `palette` for generated body objects.
4. Run `prepare-template`, then `audit`.
5. Implement the deck-specific native mechanisms in `build/builder.mjs` from the generated scaffold.
6. Run `finalize`, mechanical QA, both visual reviews, and final QA.

For every new project, `audit` enforces both content and visual contracts. It rejects
generated copy absent from the bundled English lexicon, sentence-style titles, filler/placeholders, excessive
visible words, missing text/visual roles, raw or out-of-palette colors, text-led
anchors, generic UI families, repeated compositions, and a primary figure spanning
less than 50% or occupying less than 18% of the body zone with information-bearing
geometry. The contracts cannot be disabled or weakened from `labdeck.json`. These are fail-closed
recurrence guards; full-size visual review still decides whether the figure is
intuitive and presentation-ready.

Normal `qa` also has a separate user-acceptance gate. A mechanically valid deck is
not handoff-ready while `qa.user_acceptance.status` is `pending`; after reviewing
fresh full-size renders, record `reviewer`, `accepted_at`, and the exact final
`reviewed_deck_sha256`. Structural QA, visual review, and user acceptance are
reported as separate statuses.

```bash
python3 scripts/lab_slides.py prepare-template /absolute/path/to/labdeck.json
python3 scripts/lab_slides.py audit /absolute/path/to/labdeck.json
python3 scripts/lab_slides.py finalize /absolute/path/to/labdeck.json
python3 scripts/lab_slides.py qa /absolute/path/to/labdeck.json --skip-review-gate
# write fresh Pass A and Pass B reports using the emitted hashes and renders
python3 scripts/lab_slides.py qa /absolute/path/to/labdeck.json
```

Read [workflow.md](references/workflow.md) for the full artifact sequence and [template-native.md](references/template-native.md) for the frame-map contract.

## Exact template-native contract

When `mode: exact-clone-edit`:

- Inspect every source slide. The source PPTX, preview, template profile, and SHA are visual provenance.
- Map every output slide to an exact `sourceSlide`, narrative role, density budget, visual anchor, and routing rationale.
- Resolve inherited `editTargets`; all unlisted objects default to `keep`.
- Build `template-starter.pptx` by duplicating mapped source slides. The builder imports this starter, never a fresh presentation.
- Edit inherited title/subtitle objects in place. New primitives are allowed only inside an explicit `zone` with a reason and `mustNotOverlapInherited: true`.
- Preserve original font family, size, weight, line/paragraph spacing, insets, alignment, master/layout relationship, logo, rail, top rule, and image crop unless a deviation is approved and logged.
- If copy does not fit, shorten, split, or remap. Do not silently shrink type or cover the template with a parallel custom layout.
- After `prepare-template`, `audit` measures every mapped `title_claim` against the actual slide-level starter title object. It uses that object's bbox, insets, first run size/style, and a matching local font through Pillow; an inherited layout/master duplicate is never used as the measurement target. Clear wrap/height overflow blocks `finalize` and is recorded in `reports/title-fit-preflight.json`.
- If the exact template font cannot be measured locally, the title check is explicitly `skipped` with an audit warning instead of silently substituting another family. Treat that warning as unverified typography and close it through full-size visual review or by installing the exact font.
- Run both the Presentations `check_template_fidelity.mjs` gate and `scripts/check_locked_template.py`. The strict checker compares slide routing, master/layout/theme semantics, locked slide objects, mapped text-only rewrites, and declared bounded additions.

For the retained body frame, bounded insertion is restricted to the inherited body zone recorded in the generated template profile. The builder rejects declared elements outside that zone.

## Plan and design declaration

Before layout work, state the internal communication job and choose a narrative arc appropriate to the research question. Every slide advances that arc with one narrative job, one short keyword title, and one dominant figure. Put the full claim in the figure, evidence relationship, or speaker notes—not in the title.

Every schema-v2 slide-plan entry needs:

```json
{
  "slide": 2,
  "narrative_job": "mechanism explanation",
  "title_claim": "Memory Coalescing",
  "template_frame": {
    "role": "content",
    "source_slide": 2,
    "layout_family": "single-mechanism",
    "density_budget": "medium",
    "routing_rationale": "The supplied content shell preserves the lab title and chrome while leaving one mechanism canvas."
  },
  "visual_anchor": "fixed-coordinate lanes, addresses, and one highlighted transaction delta",
  "visual_contract": {
    "anchor_type": "mechanism",
    "family": "address-lanes",
    "content_basis": ["k2-time", "k2-sectors"],
    "focus_target": "single merged memory transaction",
    "repeat_group": ""
  },
  "native_elements": [
    {
      "type": "shape",
      "name": "scattered-access",
      "visual_role": "diagram-node",
      "position": {"left": 130, "top": 170, "width": 240, "height": 350},
      "fill": "soft",
      "line": {"fill": "primary", "width": 2}
    },
    {
      "type": "text",
      "name": "lane-label",
      "text_role": "figure-label",
      "position": {"left": 150, "top": 190, "width": 200, "height": 32},
      "text": "Lane Addresses",
      "style": {"color": "ink", "fontSizePt": 18, "bold": true, "alignment": "center"}
    },
    {
      "type": "shape",
      "name": "lane-0",
      "visual_role": "data-mark",
      "text_role": "figure-label",
      "position": {"left": 155, "top": 245, "width": 190, "height": 46},
      "fill": "surface",
      "line": {"fill": "primary", "width": 1.5},
      "text": "0x00",
      "textStyle": {"color": "ink", "fontSizePt": 17, "alignment": "center"}
    },
    {
      "type": "shape",
      "name": "lane-1",
      "visual_role": "data-mark",
      "text_role": "figure-label",
      "position": {"left": 155, "top": 305, "width": 190, "height": 46},
      "fill": "surface",
      "line": {"fill": "primary", "width": 1.5},
      "text": "0x04",
      "textStyle": {"color": "ink", "fontSizePt": 17, "alignment": "center"}
    },
    {
      "type": "shape",
      "name": "lane-2",
      "visual_role": "data-mark",
      "text_role": "figure-label",
      "position": {"left": 155, "top": 365, "width": 190, "height": 46},
      "fill": "surface",
      "line": {"fill": "primary", "width": 1.5},
      "text": "0x08",
      "textStyle": {"color": "ink", "fontSizePt": 17, "alignment": "center"}
    },
    {
      "type": "shape",
      "name": "lane-3",
      "visual_role": "data-mark",
      "text_role": "figure-label",
      "position": {"left": 155, "top": 425, "width": 190, "height": 46},
      "fill": "surface",
      "line": {"fill": "primary", "width": 1.5},
      "text": "0x0C",
      "textStyle": {"color": "ink", "fontSizePt": 17, "alignment": "center"}
    },
    {
      "type": "shape",
      "name": "memory-path",
      "geometry": "rightArrow",
      "visual_role": "connector",
      "position": {"left": 370, "top": 325, "width": 520, "height": 40},
      "fill": "primary",
      "line": {"fill": "primary", "width": 1}
    },
    {
      "type": "shape",
      "name": "merged-access",
      "visual_role": "diagram-node",
      "position": {"left": 890, "top": 170, "width": 240, "height": 350},
      "fill": "focus",
      "line": {"fill": "primary", "width": 2}
    },
    {
      "type": "text",
      "name": "transaction-label",
      "text_role": "figure-label",
      "position": {"left": 930, "top": 270, "width": 210, "height": 48},
      "text": "One Transaction",
      "style": {"color": "ink", "fontSizePt": 20, "bold": true, "alignment": "center"}
    }
  ],
  "coverage": ["memory coalescing"],
  "evidence_refs": ["k2-time", "k2-sectors"],
  "notes_ref": "slide-02"
}
```

Inherited body rewrites are title-only by default. Keep body labels, sources,
code, and equations in role-tagged native elements; never route prose through
arbitrary `content.body`, `content.footer`, or `content.blurb` fields. The
cover alone may also use compact `subtitle`, `meeting_subject`, `date`, or
`author` metadata.

For incremental kernels, also record the predecessor, exact changed code line, unchanged objects, mechanism visual, and evidence. Keep coordinates stable across consecutive slides and ghost the previous state so the delta is immediately visible.

`content/design-system.json` must declare the visual thesis, inherited system, source palette, closed active palette, section rhythm, figure strategy, subject-specific signature, and explicit anti-patterns. In template-native mode this declaration explains how the inherited system will be used; it does not authorize new fonts, colors, decorative components, or prose.

## Composition and editability

Use one canvas composition, not a component-library interface. Start with the figure and add only the labels needed to read it. Avoid generic card grids, pills, badges, faux navigation, decorative metric strips, repeated icon blurbs, gradients, shadows, section color changes, and ornamental rules. Do not add filler copy, decorative icons, or invented data.

The inherited template may legitimately use a pattern or Arial typography that a generic anti-slop list would reject. The approved template wins. Judge whether a treatment is source-authentic and meaningful, not whether a font appears on a blacklist.

Native editable shapes are appropriate for technical mechanisms: arrays, lanes, arrows, memory paths, code deltas, tables, charts, and simple hardware abstractions. Use a native `rightArrow` shape for a visibly directional simple flow in the shipped scaffold; free-line arrowhead metadata is not render-proven. For attached or routed connectors, use a project-specific builder and verify the rendered arrowhead. For paper figures, isolate the one relevant panel, enlarge labels/axes, remove irrelevant series and gridlines, and rebuild annotations for presentation scale. Decorative programmatic illustration, fake screenshots, fake products, fake scientific evidence, and pseudo-official logos are not. Use authentic raster assets for photographs, screenshots, sourced figures, and approved illustration. A slide-sized raster wrapper is Critical in native mode.

Visual roles are declarations, not proof. `boundary` and `annotation`
geometry never count toward figure dominance. Primitive plots need one
horizontal and one vertical line axis plus at least two numeric or source-bound
`data-mark` elements. Native chart/plot objects need numeric series/data or a
bound source reference; label-only arrays are not data.

Create connectors before their nodes. Keep technical body text and diagram labels at least 16 pt unless the source template explicitly establishes another readable size. Keep generated copy English; inspect raster figures so embedded non-English labels are translated or replaced. Locked inherited institutional marks are the only routine language exception.

In the generated scaffold, specify native text size as `fontSizePt`. `fontSize` is the Artifact Tool's CSS-pixel unit; the scaffold converts points at 96/72 and enforces `style.minimum_body_pt`. Use semantic color tokens such as `primary`, `focus`, `soft`, and `ink`; raw hex colors are rejected. The scaffold supports bounded `text`, `shape`, and editable `line` primitives and creates line primitives before nodes. Attached connectors, charts, tables, or other advanced authoring requires a project-specific builder and fresh strict fidelity plus dual visual review; there is no unchecked custom callback.

## Evidence profile

Measurement is opt-in. Read [measurement-policy.md](references/measurement-policy.md) before running or interpreting a benchmark.

- Use physical Device 3 only on `ssh l40s-yunm` through `lab_slides.py gpu`.
- Keep timing, Nsight Compute attribution, and Nsight Systems decomposition separate.
- Label claims `CUDA EVENTS`, `NSIGHT COMPUTE`, `NSIGHT SYSTEMS`, `DERIVED`, `CODE-DERIVED`, `VENDOR SPEC`, or `INFERENCE`.
- Never use profiler replay duration as headline timing or turn counter correlation into a unique causal claim.
- Mechanism slides show the changed mechanism, measured consequence, and appropriately bounded interpretation together.

## Speaker notes

Replace the retained template's sample/authoring note unless the slide plan explicitly chooses `mode: preserve` with a specific `preserve_rationale`. Known sample notes, including the retained cover's authoring note, are rejected even in preserve mode.

Use role-aware budgets instead of padding every slide to the same length:

- cover, divider, closing: normally 20–100 words;
- mechanism and evidence: normally 90–190 words;
- appendix/reference: normally 40–120 words;
- ordinary content: normally 60–170 words.

Write every note in English. Explain the slide's purpose and transition, then add mechanism, numerical meaning, provenance, and caveats only when present. Never invent interpretation or pad notes to satisfy a word-count rule.

## HTML-assisted native mode

Do not use a PPTX → HTML → PPTX roundtrip as the default repair path. It can lose masters, layouts, DrawingML, chart semantics, line metrics, notes, and editability.

HTML can still help:

1. Initialize with `--html-prototype`; this persists `deck.authoring_mode: html-assisted-native` and a fail-closed prototype contract.
2. Run `prepare-template`, render the source frame, and build a disposable 1280×720-equivalent HTML prototype constrained to the approved body zone, fonts, colors, and density budget.
3. Run `slides-grab validate`, render PNGs, and apply the dual design gate.
4. After approval, declare the accepted composition as `native_elements` and generate `content/native-rebuild-manifest.json` with `scripts/native_rebuild_manifest.py generate`. The manifest hash-pins the HTML, prototype render, starter, frame map, plan, and native element projection.
5. Reimplement the composition in `template-starter.pptx` with native objects. The PPTX builder receives the manifest, never the HTML; using the prototype render as a final asset is rejected.
6. Run `audit`, template fidelity, editability, render, notes, and package QA on the PPTX. A stale or missing native-rebuild manifest blocks finalization.

If the user explicitly chooses direct HTML-to-PPTX conversion, label it experimental and partially editable. Raster export preserves appearance but not editability; text export is best-effort and does not preserve the original master/layout contract. Read [html-assisted-native.md](references/html-assisted-native.md).

## Design and handoff gates

Render every slide full-size after material layout, type, color, density, or imagery changes. Run two independent read-only reviews against the current renders:

- Pass A: template fidelity, frame map, locked chrome, closed-palette compliance, English-copy compliance, editability, claim truth, and no unplanned overlays.
- Pass B: audience comprehension, keyword-title quality, figure-first reading, 3–5 second takeaway, consistent color semantics, label legibility, pacing, and overlap.

Critical findings block delivery. Fix Major findings or obtain explicit user acceptance. Track deferred Minor/Note findings in `reports/design-debt.md`. Reviews are stale after any material edit; regenerate renders and both reports. The user-acceptance record is still required for a new project even when Pass A/B are clean; it is the explicit human check against color drift, filler, weak figures, repetition, unjustified whitespace, dense limitations, and title/logo breathing that static gates cannot fully judge.

LibreOffice is probe-only by default. Never promote its roundtrip automatically: it can change paragraph margins, layout relationships, and object positions even when slide count and notes survive.

Deliver one immutable final PPTX, QA report, template-fidelity report, and concise measurement-scope statement. Preserve the source template and raw evidence. Use the presentation citation format required by the Presentations skill.

## Bundled resources

- `assets/lab-meeting-template.pptx` and `assets/lab-meeting-template-preview.png`: retained default template and verified cover preview.
- `assets/style-manifest.json`: template hash, source-theme provenance, closed semantic body palette, locked chrome, and bounded body zone.
- `assets/english-words.txt` and `assets/english-technical-terms.txt`: deterministic English-copy lexicon and research-computing supplement.
- `assets/english-verbs-wordnet-index.txt`, `assets/english-verbs-wordnet-exceptions.txt`, and `assets/english-nouns-wordnet-exceptions.txt`: Princeton WordNet 3.1 verb lemmas/forms and irregular plurals used to distinguish finite-clause titles from common research keyword endings; the copied index preserves the WordNet license.
- `assets/template-builder-scaffold.mjs`: native starter import/edit/export spine with bounded element checks.
- `scripts/check_locked_template.py`: strict starter/final comparison for routing, template core, locked objects, mapped rewrites, and bounded native additions.
- `scripts/native_rebuild_manifest.py`: hash-pinned one-way HTML-prototype-to-native boundary.
- [qa-gates.md](references/qa-gates.md): exact mechanical and dual-review contract.
- [slides-grab-adaptation.md](references/slides-grab-adaptation.md): retained orchestration ideas and the HTML boundary.
