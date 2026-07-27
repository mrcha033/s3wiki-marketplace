# Measurement policy

Run measurements only when the user asks for fresh evidence or the deck genuinely depends on it.

## Before running

- confirm the intended host and physical device;
- confirm the expected GPU name and UUID when available;
- avoid disrupting other users or existing jobs;
- record the command, environment, and output needed to interpret the result.

The bundled `gpu` command is configured for physical Device 3 on `l40s-yunm`. Treat that as a project default, not permission to use another host or device.

## Timing

Use CUDA events for kernel or GPU interval timing when appropriate. Warm up first and collect enough samples to report a stable statistic. State whether setup, transfers, synchronization, and launch overhead are included.

Do not use Nsight Compute replay duration as the headline runtime. Its value is counter collection and mechanism attribution.

## Profilers

- Nsight Compute: counters and kernel-level attribution.
- Nsight Systems: launch, transfer, synchronization, and timeline decomposition.

Profiler runs may perturb execution. Keep them separate from the timing run.

## Claims

Label evidence accurately:

- `CUDA EVENTS`
- `NSIGHT COMPUTE`
- `NSIGHT SYSTEMS`
- `DERIVED`
- `CODE-DERIVED`
- `VENDOR SPEC`
- `INFERENCE`

Record the source and the limited use supported by that evidence. Correlation between counters and time supports a bounded explanation, not a unique causal claim.

## Presentation

Show the mechanism, the measured consequence, and the caveat together. Do not display false precision, mix devices or environments, or compare numbers collected under different scopes without saying so.
