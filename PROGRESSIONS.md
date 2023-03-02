# Progression Files

The `data/progressions/` directory contains a list of chord progressions by style that can be loaded
and used to generate music.

# Format

The progressions file format is a series of chords and/or single notes separated by a comma.  A
newline terminates the progression.

The `mingus` library is used to parse the chord names and translate them to MIDI integer values.

It is simple fromat and can be described as:

```txt
<chord|note>, <chord|note>, ...(\n end progression 1)
<chord|note>, <chord|note>, ...(\n end progression 2)
```

Example:
```txt
Amin11, D7, Fmaj7, Cmaj7
Amin11, D7, Fmin7, Cmaj7
```

Note that the octave is not described here and that is up to the programmer to determine the octave
for each item in the list.
