# Template-native PPTX workflow

## Contents

- Project layout
- Stage 0: environment and input intake
- Stage 1: plan, design declaration, and frame map
- Stage 2: evidence
- Stage 3: native build
- Stage 4: notes and compatibility
- Stage 5: mechanical QA and dual review
- HTML-assisted native branch
- Stage 6: handoff

## Project layout

`lab_slides.py init` creates one non-destructive project per deck:

```text
project/
├── labdeck.json
├── content/
│   ├── outline.md
│   ├── slide-plan.json
│   ├── claims.json
│   ├── notes.json
│   ├── design-system.json
│   ├── template-profile.json
│   └── template-frame-map.json
├── build/
│   └── builder.mjs
├── evidence/
│   ├── raw/
│   └── normalized/
├── output/
├── render/
│   └── final/
├── reports/
│   ├── pass-a.md
│   ├── pass-b.md
│   └── design-debt.md
└── work/
    └── template/
        └── template-starter.pptx
```

The JSON and Markdown files are declarative inputs. `builder.mjs` is the editable-PPTX implementation. Keep the user's source deck, the visual template, raw evidence, generated starter, and final output as distinct artifacts.

## Stage 0: environment and input intake

1. Read the Presentations skill, its content rules, and its template-following reference completely.
2. Run `lab_slides.py doctor`. Use the bundled Node/Python/Artifact Tool paths it reports. LibreOffice is optional and probe-only; its absence must not trigger a different authoring route.
3. Register the current/content deck separately from the template PPTX. Hash both. Never overwrite either source.
4. Run `inspect-template` when adopting or changing a template. Inspect all source slides, rendered previews, layouts, object reports, and notes before planning.
5. Use a distinct final filename.

The retained S3/Yonsei template is the default when `--template-pptx` is omitted. It has two proven source frames: slide 1 is the cover and slide 2 is the content shell. An unused layout name is not a proven frame.

## Stage 1: plan, design declaration, and frame map

Write the internal communication job, coverage matrix, and narrative before layout. Review `content/design-system.json`: keep the inherited source palette as provenance, approve one closed semantic body palette, preserve typography/chrome, and declare the figure strategy and anti-patterns. Generated visible copy and notes are English.

Every schema-v2 slide-plan entry maps to a real source slide:

```json
{
  "slide": 2,
  "narrative_job": "mechanism explanation",
  "title_claim": "Lane Compaction",
  "template_frame": {
    "role": "content",
    "source_slide": 2,
    "layout_family": "single-mechanism",
    "density_budget": "medium",
    "routing_rationale": "The supplied content shell keeps the lab chrome and leaves one bounded mechanism canvas."
  },
  "visual_anchor": "fixed-coordinate lanes and one highlighted address delta",
  "visual_contract": {
    "anchor_type": "mechanism",
    "family": "address-lanes",
    "content_basis": ["k2-time", "k2-instructions"],
    "focus_target": "compacted active lanes",
    "repeat_group": ""
  },
  "native_elements": [
    {
      "type": "shape",
      "name": "active-lanes",
      "visual_role": "diagram-node",
      "text_role": "figure-label",
      "position": {"left": 150, "top": 175, "width": 950, "height": 350},
      "fill": "soft",
      "line": {"fill": "primary", "width": 2},
      "text": "Active lanes"
    }
  ],
  "coverage": ["parallel reduction"],
  "evidence_refs": ["k2-time", "k2-instructions"],
  "notes_ref": "slide-02"
}
```

For the retained template, route the opening to source slide 1 and every body slide to source slide 2. The generated frame map resolves inherited edit targets and keeps all unlisted objects. Any new primitive needs a bounded insertion zone, a reason, and `mustNotOverlapInherited: true`.

Run:

```bash
python3 scripts/lab_slides.py prepare-template /absolute/path/to/labdeck.json
python3 scripts/lab_slides.py audit /absolute/path/to/labdeck.json
```

`prepare-template` duplicates the mapped source slides into `work/template/template-starter.pptx`. `audit` rejects a stale template hash, stale frame map, missing starter, unbounded additions, incomplete communication decisions, and builders that create a fresh presentation. It also enforces dictionary-backed English copy, keyword titles, role-bound visible copy, filler and word budgets, semantic palette tokens, a primary figure spanning at least 50% and occupying at least 18% of the body zone with authenticated information-bearing geometry, content/source basis, and composition diversity. Boundary/annotation rectangles do not count; plots need numeric or source-bound data and valid primitive axes when applicable. The audit writes `reports/title-fit-preflight.json`, `reports/content-contract.json`, and `reports/visual-contract.json`. A title that needs more lines than the inherited box permits fails before `finalize`; a missing measurement font is an explicit warning/skip that still requires visual closure.

## Stage 2: evidence

Measurement is opt-in. Existing evidence is reusable only if all of these match:

- physical GPU index and UUID;
- source and binary hash;
- compiler and flags;
- workload size, data type, semantics, and initialization;
- warmups, samples, process count, and aggregation;
- profiler tool/version and metric set.

Use `lab_slides.py gpu` for every L40S command. Split timing, Nsight Compute, and Nsight Systems into separate runs. Save raw output and a run manifest. Normalize to CSV/JSON and add claims to `content/claims.json`.

## Stage 3: native build

The builder imports the prepared starter and exports the edited presentation. It must not call a fresh-presentation constructor or add unmapped slides. `finalize` supplies:

- `INPUT_PPTX` — the exact prepared `template-starter.pptx`;
- `OUTPUT_PPTX`;
- `LABDECK_CONFIG`;
- `LABDECK_CLAIMS`;
- `LABDECK_SLIDE_PLAN`;
- `LABDECK_TEMPLATE_MAP`;
- `LABDECK_TEMPLATE_PROFILE`;
- `LABDECK_DESIGN_SYSTEM`.

Edit mapped inherited title/subtitle targets in place. Preserve the master/layout relationship, logo, rail, top rule, font metrics, paragraph spacing, insets, and image crops. Add native editable arrays, lanes, arrows, tables, charts, code deltas, and technical shapes only inside the approved body zone. Use only semantic palette tokens. Every text-bearing element needs a `text_role`; every non-text element needs a `visual_role`. If content does not fit, shorten, split, or remap it; do not hide the template under a slide-sized overlay.

## Stage 4: notes and compatibility

`finalize` writes an Artifact Tool PPTX, copies it to the visual stage by default, then attaches speaker notes to the final PPTX. Keep `build.compatibility_roundtrip: false` unless the user has explicitly accepted a proven conversion. LibreOffice may change paragraph margins, layout relationships, and object positions even when the package still opens.

Write notes in English and use role-aware ranges instead of padding every slide:

- cover/divider/closing: concise framing and transition;
- mechanism/evidence: fuller explanation, provenance, and caveats;
- appendix/reference: compact retrieval context;
- ordinary content: enough narration to make the slide self-contained.

Replace the retained template's sample note. Use `mode: preserve` only with a specific `preserve_rationale`; known sample/authoring notes are rejected even when preservation is requested.

## Stage 5: mechanical QA and dual review

Run `qa --skip-review-gate` to create full-size renders, a montage, package/overflow results, source fingerprints, a render manifest, and both template-fidelity reports. The bundled Presentations gate checks the authoring route and overlays; `check_locked_template.py` additionally compares slide routing, template-core semantics, inherited layers, locked slide objects, mapped text-only rewrites, and one-to-one bounded native additions.

Dispatch two independent read-only reviewers against every full-size PNG:

- Pass A: template fidelity, editability, frame-map integrity, English copy, closed-palette provenance, claim truth, and anti-slop.
- Pass B: keyword-title quality, audience comprehension, figure-first reading, consistent color semantics, label legibility, pacing, and overlap.

Each report must quote the current deck SHA-256, render-manifest SHA-256, and source-manifest SHA-256. A material edit invalidates all three fingerprints and both reviews. After fixes, rerender and replace the stale reports, then run normal `qa`.

Normal `qa` additionally requires a human acceptance record for new projects:
`qa.user_acceptance.status=accepted`, a reviewer and timestamp, and the exact
final-deck SHA. `--skip-review-gate` is diagnostic only and intentionally leaves
visual review and user acceptance unresolved.

The QA LibreOffice roundtrip is a disposable compatibility probe. It may verify slide count and notes digest, but it is never promoted to the final source automatically.

## HTML-assisted native branch

HTML is optional, disposable composition tooling. Initialize with `--html-prototype`, constrain the prototype to the inspected canvas, body zone, inherited tokens, and density budget, and validate/review its render. After `prepare-template`, generate the hash-pinned `content/native-rebuild-manifest.json`; only then reconstruct the accepted composition with native objects in `template-starter.pptx`. The manifest validator blocks stale prototypes, direct conversion, full-slide raster reuse, and mismatched native element projections. Do not roundtrip the original PPTX through HTML as the default repair path.

Direct HTML-to-PPTX or slide-sized raster export is an explicit fallback only. Label it experimental and partially editable, record the lost master/layout/editability guarantees, and obtain user acceptance before delivery.

## Stage 6: handoff

Deliver:

- one final editable PPTX;
- QA and template-fidelity reports plus the review montage;
- a compact measurement-scope statement;
- changed-slide citations;
- any deferred design debt.

Structural QA, Pass A/B visual review, and user acceptance are separate claims in
the handoff. A green mechanical report alone is not an aesthetic acceptance.

Do not deliver the starter, artifact, LibreOffice probe, or HTML prototype unless the user asks for diagnostic intermediates.
