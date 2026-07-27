# Motion and domain visuals

Motion is optional. Use it only when the audience needs to see an interaction unfold.

Good uses:

- a request moving through a serving pipeline;
- a syscall crossing user and kernel space;
- a scheduler admitting and completing work;
- data moving between memory tiers;
- a before/after state transition.

Use a static diagram for architecture, taxonomy, ownership, or any point that does not depend on time.

## Included Manim scenes

The skill includes:

- `serving`: router, queue, scheduler, GPU, and token flow;
- `syscall`: user, syscall, VFS, page cache, device, and completion path.

Render a preset:

```bash
python3 scripts/motion_assets.py render \
  --project /absolute/path/to/project \
  --preset syscall \
  --output assets/motion/syscall.gif \
  --palette /absolute/path/to/style-manifest.json
```

For a custom scene:

```bash
python3 scripts/motion_assets.py render \
  --project /absolute/path/to/project \
  --source /absolute/path/to/scene.py \
  --scene MyScene \
  --output assets/motion/my-scene.mp4
```

The helper writes the requested media and a poster PNG. `inspect` prints basic duration, size, and dimensions.

## Authoring guidance

- Keep the background and labels consistent with the active deck.
- Use a small number of states.
- Make the start and end frames useful on their own.
- Avoid decorative motion and continuous background activity.
- Keep labels large enough for the slide.
- Do not animate a claim beyond what the sources support.

When PowerPoint playback or portability is uncertain, use the poster frame in the deck and provide the MP4 as a companion.
