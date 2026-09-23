# Room generator

Every room in the game is modelled here in Python with Blender, lit by a Cycles bake,
and written to `game/rooms/` as `<name>.json` (layout, plus the meshes as base64) and day and
night lightmaps (`<name>_day.webp`, `<name>_night.webp`).

## Setup

- Python 3.11 and `pip install bpy==5.0.1` (Blender as a module; CPU Cycles is enough)
- Open Image Denoise 2.3.3 from its GitHub releases. `lib.py` looks for
  `oidnDenoise` in `/tmp/oidn-2.3.3.x86_64.linux/bin/`, or set `OIDN=/path/to/oidnDenoise`

## Building

    python3 rooms/build.py tower            # full bake, day and night
    python3 rooms/build.py tower --quick    # low sample count, for checking a layout
    rooms/bake_all.sh rest well tower       # several full bakes, one after another

`r_<name>.py` holds each room; `lib.py` has the shared kit (door sockets, arches, pools,
shelves, stairs, ramps), the bake and the export. A 1x1 room takes 2 to 4 minutes on
4 cores; the big 2x2 rooms take 15 to 25.
