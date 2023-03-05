# mdcmp

mdcmp (MIDI Composer) is a Python library for easily generating songs and emitting MIDI files.

**This is a work in progress.**

* [MDC file format spec](/docs/MDC_FORMAT_SPEC.md)
* [Progressions spec](/docs/PROGRESSIONS.md)
* [Grid](/docs/GRID.md)

# TODO

- Load MDC file: Convert mdc file back to grid

- Composition:
    - Create the Composition class.
    - Build a mdc bank of canned beats and progressions.
    - Load banks, glob style.
    - Generate random song from selected progressions.
    - Generate intros, verses, bridges, breakdown, chorus, outro.
    - Fade tracks out.
    - Fade tracks in.
    - Humanize: Add some velocity and timing micro-shifts.
    - Drums: Fills.

- CLI:
    - Convert: translate mdc files to midi files via CLI.
    - Compose from cli by specifying layers, loops, and params to composition object.
    - Example idea of CLI composer usage:
```
mdc-compose \
    --load samples/lofi/ \
    --out name.midi \
    --loop-all 2 \
    --layer intro=drums1:lofi2,verse=drums1:lofi3  \
    --loop-layer-order intro:2,verse:10,intro:2,verse:10 \
    --velocity-jitter 13 \
    --fade-in 10 --fade-out 10 \
    --auto-dynamics [0-10] \
    --humanize
```
