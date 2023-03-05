# MDC File Format - Version 1

The MDC file format is a text based format that describe what, where, how, and when notes are played
in a MIDI file. It is useful for serializing compositions to a file, which then can be used as a
collection of loops/songs to input into mdcmp or shared with others.

The file format follows this structure:
```
version(int)
reserved|track-type|granularity|start-offset| track-data...
reserved|track-type|granularity|start-offset| track-data...
...
```

- Version header (int) -- The MDC file format version. This is the first line of the file.
- Track info:
    - Reserved (reserved) -- A reserved info slot for future use.
    - Track type (string) -- The type of track. This can be either "drum" or "instrument".
    - Granularity (char) -- The grid granularity. Options:
        half: "h"
        quarter: "q"
        eighth: "e"
        sixteenth: "s"
        thirtysecond: "t"

    - Start offset (float) -- The offset in time that the track starts.
- Track data:
    - Pitch list (list of string or int) -- A list of pitches to play at this position.
    - Duration (list of str) -- The duration of the note represented as a shorthand note value.
        double-whole: "W"
        whole: "w"
        half: "h"
        half-dotted: "h."
        quarter: "q"
        quarter-dotted: "q."
        eighth: "e"
        eighth-dotted: "e."
        sixteenth: "s"
        sixteenth-dotted: "s."
        thirtysecond: "t"
    - Additional offset (list of char) -- Add an additional amount of time before the note
      position. A value of "n" for 0 or none can be specified in addition to the duration values.
    - Velocity (list of int) -- The velocity of the position. A value from 0 (silent) to 127 (max MIDI
      value).
    - Volume (int) -- Overall volume of the track. "n" for noop.
    - Pitchwheel (int) --Pitchwheel control. Humanized from -64 to 64. "n" for noop.
    - Modwheel (int) -- Modulation control. 0 is off, otherwise a value 1-127. "n" for noop.
    - Expression (int) -- Expression control. 0 is off, otherwise a value 1-127. "n" for noop.
    - Sustain (int) -- Toggle 0=off, 1=on. "n" for noop.
    - Pan (int) -- A range of -64 to 64. "n" for noop.

Note that each track data is a list of X. Lists are delimited by `!`.  If a `!` is not specified,
it will use a single value for all items previously supplied as a list or a single item.

# Examples

This example creates two instrument tracks that will play together.  The first note is a chord of
multiple pitches played at the same time.  The the following notes are single pitches. The output
of this will be two separate MIDI tracks.

Create two instrument tracks on a quarter note grid:
```
1
_|instrument|q|0.0| 33!55!44,q,n,50!45!30,n,n,n,n,n; 60,q,n,45,n,n,n,n,n; 58,q,n,50,n,n,n,n,n;
_|instrument|q|0.0| 33,q,n,20,n,n,n,n,n; 60,q,n,25,n,n,n,n,n; 28,q,n,20,n,n,n,n,n; 0,q,n,0,n,n,n,n,n;
```


This example creates a drum track and instrument track on an eighth note grid:
```
1
_|drum|e|0.0| 36!42!,q!e,n,50!40,n,n,n,n,n; 42,e,n,50,n,n,n,n,n; 38!42,q!e,n,50,n,n,n,n,n; 42,e,n,50,n,n,n,n,n;
_|instrument|e|0.0| 33,e,n,50,n,n,n,n,n; 35,e,n,50,n,n,n,n,n; 33,e,n,50,1,n,n,n,n,n; 32,e,n,50,n,n,n,n,n;
```
