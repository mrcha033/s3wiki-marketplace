# Motion and domain visual grammar

## Contents

- Routing
- Motion contract
- Semantic primitives
- Systems and OS archetypes
- AI-serving archetypes
- Evidence and metrics
- PowerPoint delivery boundary
- External precedents

## Routing

Use a visual only when it makes a relationship easier to understand than concise
English labels and narration. Choose in this order:

| Need | Route | Reason |
|---|---|---|
| fixed topology, hierarchy, ownership, comparison | native static | editable and universally readable |
| two or three discrete states | progressive native slides | preserves exact coordinates and works in every PowerPoint surface |
| continuous queueing, concurrency, state transfer, or overlap | Manim GIF | motion directly explains time and interaction |
| high-detail or long-form playback outside the deck | companion H.264/AAC MP4 | better compression and timing, with a poster in the PPTX |

Do not animate a static architecture merely to add movement. A motion scene must
answer a question that includes time: what enters, waits, owns, blocks, wakes,
moves, overlaps, or completes?

## Motion contract

- One scene proves one interaction.
- Storyboard the initial state, focal transition, and terminal state before code.
- Keep component positions stable. Move or morph the state token, not the entire
  diagram.
- Use 3–8 seconds, one clip per slide, no more than five moving tokens, and no
  more than 8 MB for an embedded GIF.
- Use motion on at most 25% of the deck, with one clip allowed for short decks.
- Keep labels to English keywords or noun phrases. Do not add subtitles,
  narration text, kinetic type, decorative counters, or slogans.
- Use only `background`, `surface`, `ink`, `muted`, `primary`, `focus`, and
  `soft`. `focus` identifies the current event; previous states return to
  `surface` or `muted`.
- Render a low-quality smoke test first. Inspect the initial, focal, and final
  frames before the production render.
- Render the scene with the current project's seven active-palette tokens. The
  bundled scenes read these tokens from the renderer environment; do not copy
  their retained-template fallback hex values into a custom-template scene.
- For GIF delivery, render Manim to MP4 first, generate an explicit compact GIF
  palette, and apply it with dithering disabled. Validate decoded pixels against
  blends of the project palette; chromatic quantization drift is a release
  blocker.
- Register the scene source, supplied source IDs, media, start poster, end-state
  PNG, duration, delivery mode, domain, archetype, fallback, and English alt
  text in `content/motion-assets.json`.
- Motion may illustrate a supplied mechanism. It is not evidence and must not
  invent latency, queue depth, cache occupancy, throughput, or hardware detail.

## Semantic primitives

Use a small, stable vocabulary across static and motion visuals:

| Primitive | Meaning |
|---|---|
| container | ownership or protection boundary |
| lane | time, resource, thread, stream, rank, or stage |
| queue | ordered waiting work with explicit ingress and egress |
| token | one request, page, cache line, tensor, batch slot, or state |
| solid arrow | data movement |
| dashed arrow | control, invalidation, wake-up, or dependency |
| boundary crossing | syscall, RPC, DMA, device, or process transition |
| focus fill | the one current change |
| muted/ghost state | unchanged predecessor |

Keep one abstraction level per visual. Do not mix deployment nodes, kernel
internals, cache-line state, and benchmark results in one canvas. If the
interaction needs more than roughly six components or three edge classes, split
it into overview and mechanism slides.

## Systems and OS archetypes

### Syscall Path

Default order:

`User → Syscall → VFS → Page Cache → Driver/Device`

Show the user/kernel boundary, the request token, and the completion or wake-up
path. Do not imply that every syscall reaches storage. Label optional or cached
paths when source evidence distinguishes them.

### Scheduler State

Use lanes or a small state graph:

`Runnable → Running → Sleeping/Blocked → Runnable`

Animate one task and one wake-up source. A run queue is an ordered waiting
region; a CPU lane is a resource. Do not present conceptual timing as measured
latency.

### Memory Path

Choose one level:

- virtual address: `TLB → Page Table → Page Fault`;
- cache hierarchy: `L1 → L2 → LLC → DRAM`;
- storage fault: `Page Cache → Block Layer → Device`;
- coherence: ownership/state transition for one cache line.

Use one token for the page or cache line. Show hit/miss, eviction, invalidation,
or fill only when the source establishes it.

### Parallel Lanes

Use stable lanes for threads, processes, streams, ranks, pipeline stages, or
devices. Show synchronization as a boundary and collective/data movement as
separate edge types. Keep unchanged lanes fixed across incremental slides.

### Trace Waterfall

Use service or thread lanes and source-bound spans. Position and duration are
evidence, so an illustrative trace must be labeled `conceptual` and must not
carry numeric axes.

### Flamegraph Zoom

Use only sourced profiler data. Preserve width as sample proportion. Animation
may zoom from a parent frame to one child path, but must not alter relative
widths or invent call relationships.

## AI-serving archetypes

### Request Flow

Default components:

`Gateway/Router → Queue → Scheduler → Worker/GPU → Token Stream`

Animate one request or a small batch. Distinguish queue admission, scheduling,
execution, and streaming. Do not use one generic arrow for all four semantics.

### Prefill Decode

Use a time or stage split:

- prefill consumes prompt tokens and creates KV state;
- decode iterates with existing KV state;
- a transfer edge appears only for a sourced disaggregated design.

Continuous batching should show requests joining or leaving a live batch while
stable decode slots remain fixed. Do not imply a specific batching policy from
generic serving behavior.

### KV Cache

Use blocks, ownership, allocation, reuse, and eviction. Animate one request's
blocks or one eviction decision. Capacity, block size, hit rate, and eviction
thresholds require source or measurement references.

### Parallel Lanes

Use one visual for tensor, pipeline, expert, or data parallelism. Label
collectives and synchronization. Avoid mixing all parallel modes unless the
slide is explicitly an architecture overview.

### Backpressure

Show queue occupancy or blocked ingress only when data exists. Otherwise use
qualitative states such as `Open`, `Queued`, and `Throttled` without numeric
scales.

### Speculative Decode

Use two aligned lanes:

`Draft → Verify → Accept/Reject`

Animate the candidate token group and the verifier decision. Acceptance rate,
speedup, or token counts must be source-bound.

## Evidence and metrics

Use AI-serving metrics with their exact meanings:

- TTFT: request arrival to first output token;
- TPOT/ITL: token-generation cadence after the first token;
- E2EL: request arrival to completion;
- throughput/goodput: completed work under the stated SLO and load;
- request rate and concurrency: workload controls, not outcomes.

Do not animate metric values unless each value is present in the claims ledger.
For a performance result, prefer a static plot or trace with units; use motion
for the mechanism that explains the result, not for decorative number changes.

## PowerPoint delivery boundary

The shipped builder can embed PNG, JPEG, and animated GIF bytes as bounded image
elements while preserving the supplied template. Desktop PowerPoint plays an
animated GIF during the slide show. PowerPoint for the web shows only a static
frame, so every GIF needs start/end proof images and a meaningful static
fallback.

The Artifact Tool has no verified native video-authoring API in this workflow.
Do not inject video relationships through direct OOXML mutation. Render MP4 as
H.264 with AAC audio or no audio, place its poster in the deck, and deliver the
MP4 beside the PPTX. Linked files can break when moved, so the handoff must state
that the MP4 is a companion asset.

The audit reads actual GIF frame delays and loop metadata, probes MP4 codec and
duration, validates both PNG proof headers and dimensions, and samples decoded
media colors. Manifest duration and `loop: true` are declarations, not proof.

## External precedents

Use principles, not palettes or copied scene code:

- ECC `manim-video`: one visual thesis, short scenes, progressive reveal,
  low-quality smoke render, and production proof frames:
  <https://github.com/affaan-m/ECC/tree/main/skills/manim-video>
- ManimCE practices and composer: transforms, updaters, timing, and GIF output:
  <https://github.com/adithya-s-k/manim_skill>
- C4 architecture and Mermaid skills: abstraction levels and a compact directed
  graph as semantic input:
  <https://github.com/softaworks/agent-toolkit>
- HyperFrames motion graphics: deterministic shot plan and start/key/end
  snapshots:
  <https://github.com/heygen-com/hyperframes/tree/main/skills/motion-graphics>
- vLLM serving metrics:
  <https://github.com/vllm-project/vllm-skills/blob/main/plugins/vllm-skills/skills/vllm-bench-serve/SKILL.md>
- NVIDIA Jetson LLM serving topology:
  <https://github.com/NVIDIA/skills/blob/main/skills/jetson-llm-serve/SKILL.md>
- Distributed tracing swimlanes:
  <https://github.com/wshobson/agents/blob/main/plugins/observability-monitoring/skills/distributed-tracing/SKILL.md>
- Grafana Pyroscope profiling semantics:
  <https://github.com/grafana/skills/blob/main/skills/grafana-lgtm/pyroscope/SKILL.md>
