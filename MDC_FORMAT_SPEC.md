# MDC File Format
The MDC file format is a text based format that describe what, where, how, and when notes are played in
a MIDI file.

The file format follows this structure:
```
version(int)
reserved|track-type|start-offset| track-data...
reserved|track-type|start-offset| track-data...
...
```

- Version header (int) -- The MDC file format version. This is the first line of the file.
- Track info:
    - Reserved (reserved) -- A reserved info slot for future use.
    - Track type (string) -- The type of track. This can be either "drum" or "instrument".
    - Start offset (float) -- The offset in time that the track starts.
- Track data:
    - Pitch list (list of string or int) -- A list of pitches to play at this position.
    - Duration (list of char) -- The duration of the note represented as a shorthand note value.
    - Additional offset (list of float) -- Add an additional amount of time before the note
      position.
    - Volume (list of int) -- The volume of the position. A value from 0 (silent) to 127 (max volume).

Note that track data is a list of X. Lists are delimited by `!`.  If a `!` is not specified, it will
use a single value for all items the specified can apply to.

# Examples

This example creates two instrument tracks that will play together.  The first note is a chord of
multiple pitches played at the same time.  The the following notes are single pitches. The output
of this will be two separate MIDI tracks.

Create two instrument tracks for three beats:
```
version 1
_|instrument|0.0| 33!55!44,q,0.0,50!45!30; 60,q,0.0,45; 58,q,0.0,50;
_|instrument|0.0| 33,q,0.0,20; 60,q,0.0,25; 28,q,0.0,20;
```


This example creates a drum track and instrument track:
```
version 1
_|drum|0.0| kick1!hat1!,q!e,0.0,50!40; hat1,e,0.0,50; snare1!hat1,q!e,0.0,50; hat1,e,0.0,50;
_|instrument|0.0| 33,e,0.0,50; 35,e,0.0,50; 33,e,0.0,50,1; 32,e,0.0,50;
```
