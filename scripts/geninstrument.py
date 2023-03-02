# this file describes how to write an composition track
# w = whole 4
# h = half 2
# q = quarter 1
# e = eigtht 0.5
# s = sixteenth 0.25
# t = thirty-second 0.125
# 0 = skip/0 value
# format: start-time-offset|pitch,note,note-additional-time,volume;...
# start-time-offset|pitch!pitch2!...,note,note-additional-time,volume;...\n
# start-time-offset|pitch,note,note-additional-time,volume;...\n
# 0|33,q,0,100;
# 1|100!50,h,0,100;
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


def chord_to_midi(chord: str, octave: int) -> list[int]:
    notes: list[str] = chords.from_shorthand(chord)
    midi_notes: list[int] = []
    for note in notes:
        midi_notes.append(note_to_midi_int(note, octave))
    return midi_notes


def gen_inst1():
    # chord_progression = ["Cmaj7", "Cmaj7", "Fmaj7", "Gdom7"]
    chord_progression = ["Am", "F", "Em", "Dm"]  # "Cmaj7", "Fmaj7", "Gdom7"]
    data = "0|"
    # 0|33,q,0,100;
    # 1|100,h,0,100;
    midi_pitches = progression_to_midi(chord_progression, 3)
    mi = 0
    for _ in range(30):
        pitch = midi_pitches[mi]
        mi += 1
        volume = random.randint(20, 90)
        if mi >= len(midi_pitches):
            mi = 0
        data += f"{pitch},q,0,{volume};"
    return data


def gen_inst2():
    chord_progression = ["Gmaj7", "Cmaj7", "Fmaj7", "Cdom7"]
    chord_progression = ["Am", "F", "Em", "Dm"]  # "Cmaj7", "Fmaj7", "Gdom7"]
    data = "0|"
    # 0|33,q,0,100;
    # 1|100,h,0,100;
    midi_pitches = progression_to_midi(chord_progression, 4)
    for _ in range(10):
        for pitch in midi_pitches:
            volume = random.randint(20, 30)
            data += f"{pitch},w,0,{volume};"
    return data


def gen_inst3():
    chords = ['Dmin11', 'Gmin7', 'Dmin11', 'Ebmin11', 'C#dim7']
    chords = ['Dmin11', 'Gmin7', 'Dmin11', 'Ebmin11', 'C#dim7', 'Ebmin11', 'Dmin11', 'Gmin7']
    midi_chords = [chord_to_midi(i, 4) for i in chords]
    data = "0|"
    for _ in range(10):
        for chord_notes in midi_chords:
            pitch = '!'.join(list(map(str, chord_notes)))
            volume = random.randint(40, 60)
            data += f"{pitch},w,0,{volume};"
    return data


def gen_inst4(chords: list[str]):
    midi_chords = [chord_to_midi(i, 4) for i in chords]
    print('>'*80)
    print(midi_chords)
    data = "0|"
    for _ in range(10):
        for n, chord_notes in enumerate(midi_chords):
            pitch = '!'.join(list(map(str, chord_notes)))
            volume = random.randint(40, 60)
            if n in (3, 4):
                data += f"{pitch},h,0,{volume};"
            else:
                data += f"{pitch},w,0,{volume};"
    # add same progression but as single quarter notes to play out the chord over time
    data += "\n0|"
    for _ in range(10):
        for n, chord_notes in enumerate(midi_chords):
            volume = random.randint(24, 48)
            note_type = '0'
            if n in (3, 4):
                # this is half
                note_type_silent = ''
                if len(chord_notes) == 2:
                    note_type = 'q'
                elif len(chord_notes) == 3:
                    note_type = 'e'
                    note_type_silent = 'e'
                elif len(chord_notes) == 4:
                    note_type = 'e'
                elif len(chord_notes) > 4:
                    note_type = 'e'
                    chord_notes = chord_notes[:4]
                for pitch in chord_notes:
                    data += f"{pitch},{note_type},0,{volume};"
                if note_type_silent:
                    data += f"0,{note_type_silent},0,0;"
            else:
                # w -> 4
                note_type_silent = ''
                if len(chord_notes) == 2:
                    note_type = 'h'
                elif len(chord_notes) == 3:
                    note_type = 'q'
                    note_type_silent = 'q'
                elif len(chord_notes) == 4:
                    note_type = 'q'
                elif len(chord_notes) == 4:
                    note_type = 'q'
                elif len(chord_notes) > 4:
                    note_type = 'q'
                    chord_notes = chord_notes[:4]
                for pitch in chord_notes:
                    data += f"{pitch},{note_type},0,{volume};"
                if note_type_silent:
                    data += f"0,{note_type_silent},0,0;"

    return data


def main():
    # gens = (gen_inst1, gen_inst2, gen_inst3)
    #chords = ['Dmin11', 'Gmin7', 'Dmin11', 'Ebmin11', 'C#dim7']
    chords = ['Cmaj7', 'Amin7', 'Dmin7', 'G7']
    gens = (gen_inst4(chords), )
    data = "\n".join([i for i in gens])
    with open(sys.argv[1], "w") as fd:
        fd.write(data)


if __name__ == "__main__":
    main()
