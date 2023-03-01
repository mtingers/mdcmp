# mdcmp

mdcmp (MIDI Composer) is a Python package for generating drum and instrument tracks and emitting
MIDI files.

**This is a work in progress.**

# Notes

## Timing Notes
```
w = whole -  4
h = half - 2
q = quarter - 1
e = eighth - 0.5
s = sixteenth - 0.25
t = thirty-second - 0.125
0 = skip/0 value - 0.0
```

## The Composer File Format


Format:
```
start-time-offset|pitch,note,note-additional-time,volume|velocity;...\n
start-time-offset|pitch,note,note-additional-time,volume|velocity;...\n
...
```

Example format:
```
0|33,q,0,100;
1|100,h,0,100;
```

## The Drum File Format

Format:
```
name|start-time-offset|note,note-additional-time,volume;...\n
name|start-time-offset|note,note-additional-time,volume;...\n
...
```

Example:
```
kick1|0|q,0,100;
snare1|1|h,0,100;
```
