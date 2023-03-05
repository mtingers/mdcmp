# Grid Overview

The goal of Grid() is to provide an easy way to generate and layer tracks of different types, then
produce an mdc data file for processing.

Key features:
    - Layer multiple notes at one bar beat.
    - Layer multiple tracks on top of each other.
    - Easily copy and repeat.
    - Apply mass transformation on groups of bars and tracks.

# Notes

- If bars 1,2 and 5 are created, the generated output will be a full rest/blank bar for bar 3-4.
- Notes are either classified as "drum" or "instrument".
- Note classification checks if value matches a drum name and uses the drum.  Otherwise, it will
  attempt to translate the note or chord into a series of midi pitches when generating the MDC
  data file.

# Granularity

When a grid is initially defined, it has a set granularity related to a type of note (e.g. half,
quarter, eighth, sixteenth, or thirtysecond).  A bar will have N beats based off of this
granularity.  For example, a granularity of half note only has 2 beats per bar, where a granularity
of quarter note has 4, and eighth has 8 beats, etc. It currently only support 4/4 time signatures,
but in the future this may change.

# Diagrams

Below is a diagram of how these are layered using a drum and instrument composition:
```
    track-1:               bar-1            bar-2
    track-1:      +-----------------------------------+
    track-1:  time| 0 1 2 3 4 5 6 7 | 0 1 2 3 4 5 6 7 |
    track-1:      +-----------------------------------+
    track-1:  kick| k       k       | k       k       |
    track-1: snare|     s       s   |     s       s   |
    track-1:   hat| h h h h h h h h | h h h h h h h h |
    track-1:      +-----------------------------------+
    ===================================================
    track-2:               bar-1            bar-2
    track-2:      +-----------------------------------+
    track-2:  time| 0 1 2 3 4 5 6 7 | 0 1 2 3 4 5 6 7 |
    track-2:      +-----------------------------------+
    track-2:      | C               |                 |
    track-2:      | Eb  Eb          |     Eb          |
    track-2:      | G               |                 |
    track-2:      | Bb              |                 |
    track-2:      +-----------------------------------+
```

# Automation controller

MAYBE TODO: Implement the following automation controller.  Right now it is grouped with the track data,
but this causes issues if multiple calls to the same bar:track:beat are called. It currently
takes the last call's event and ignores the others. Example:
```
    # This will take the last volume value "50" and is confusing since it seems like hat1/snare1
    # have an independent volume, but it is the entire volume of the track:
    grid.add(bars=[1,], tracks=[0,], beats=[1], value="hat1", duration=1, volume=100)
    grid.add(bars=[1,], tracks=[0,], beats=[1], value="snare1", duration=1, volume=50)
```

MAYBE TODO:
And each track is assigned an automation controller to change the entire track settings for volume,
pan, modwheel, pitchwheel, expression, and sustain.  Example:
```
    controller:                    bar-1            bar-2
    controller:           +-----------------------------------+
    controller:       time| 0 1 2 3 4 5 6 7 | 0 1 2 3 4 5 6 7 |
    controller:           +-----------------------------------+
    controller:        pan| 5   0   -5      | -9              | -64 - +64
    controller: pitchwheel|                 |                 | -64 - +64
    controller:     volume|                 |                 | 0 - 127
    controller:   modwheel|                 |                 | 0 - 127
    controller: expression|                 |                 | 0 - 127
    controller:    sustain| y               | n               | 0=off, >=64=on
    controller:           +-----------------------------------+
```

## Grid datastructure
```
    grid = {
        0: {                            <-- bar
            0:                          <-- track
            [                           <-- beat
                {                       <-- beat metadata
                    'velocity': N,
                    'duration': N,
                    'value': 'X',
                    ...
                }
            ],
        }
    }
```
# TODO
- Maybe add a `reshape(new_granularity)` method, but this could be difficult:
```
grid.reshape(new_granularity=Granularity.EIGHTH)
... add beats ...
grid.reshape(new_granularity=Granularity.SIXTEENTH)
```
