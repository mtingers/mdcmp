# this file describes how to write an composition track
# w = whole 4
# h = half 2
# q = quarter 1
# e = eigtht 0.5
# s = sixteenth 0.25
# t = thirty-second 0.125
# 0 = skip/0 value
# format: start-time-offset|pitch,note,note-additional-time,volume|velocity;...
# 0|33,q,0,100;
# 1|100,h,0,100;
import sys
import random
from mingus.core import chords

NOTES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
NOTES_COUNT = len(NOTES)
OCTAVES = list(range(11))
ACCIDENTALS = {
    'Db': 'C#',
    'D#': 'Eb',
    'E#': 'F',
    'Gb': 'F#',
    'G#': 'Ab',
    'A#': 'Bb',
    'B#': 'C',
}


def swap_accidental(note):
    return ACCIDENTALS.get(note, note)


def note_to_midi_int(note: str, octave: int) -> int:
    note = swap_accidental(note)
    note_int: int = NOTES.index(note)
    note_int += (NOTES_COUNT * octave)
    return note_int


def progression_to_midi(chord_progression: list[str], octave: int) -> list[int]:
    notes = []
    note_numbers = []
    for chord in chord_progression:
        notes.extend(chords.from_shorthand(chord))
    for note in notes:
        note_numbers.append(note_to_midi_int(note, octave))
    return note_numbers


def gen_inst1():
    chord_progression = ["Cmaj7", "Cmaj7", "Fmaj7", "Gdom7"]
    data = "0|"
    # 0|33,q,0,100;
    # 1|100,h,0,100;
    midi_pitches = progression_to_midi(chord_progression, 3)
    mi = 0
    for _ in range(30):
        pitch = midi_pitches[mi]
        mi += 1
        velocity = random.randint(20, 90)
        if mi >= len(midi_pitches):
            mi = 0
        data += f"{pitch},q,0,{velocity};"
    return data


def gen_inst2():
    chord_progression = ["Gmaj7", "Cmaj7", "Fmaj7", "Cdom7"]
    data = "0|"
    # 0|33,q,0,100;
    # 1|100,h,0,100;
    midi_pitches = progression_to_midi(chord_progression, 4)
    mi = 0
    for _ in range(10):
        velocity = random.randint(10, 50)
        pitch = midi_pitches[mi]
        mi += 1
        if mi >= len(midi_pitches):
            mi = 0
        data += f"{pitch},w,0,{velocity};"
    return data


def main():
    gens = (gen_inst1, gen_inst2)
    data = "\n".join([i() for i in gens])
    with open(sys.argv[1], "w") as fd:
        fd.write(data)


if __name__ == "__main__":
    main()
