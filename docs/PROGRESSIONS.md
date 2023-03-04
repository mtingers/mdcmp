# Progression Files

The `data/progressions/` directory contains a list of chord progressions by style that can be loaded
and used to generate music.

# Format

The progressions file format is a series of chords separated by a comma.  A newline terminates the
progression.

The `mingus` library is used to parse the chord names and translate them to MIDI integer values.

It is simple fromat and can be described as:

```txt
<chord>, <chord>, ...(\n end progression 1)
<chord>, <chord>, <chord>, ...(\n end progression 2)
```

Example:
```txt
Amin11, D7, Fmaj7, Cmaj7
Amin11, D7, Fmin7, Cmaj7
```
