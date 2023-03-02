from mingus.core import chords

# Map note names (e.g. q=quarter -> 1) to time values
NOTE_TYPE_MAP = {
    "w": 4,
    "h": 2,
    "q": 1,
    "e": 0.5,
    "s": 0.25,
    "t": 0.125,
    "0": 0.0,
}
# for calculating note types to duration in duration (e.g. for loop range)
NOTE_TYPE_TO_DURATION = {
    "w": 0.25,
    "h": 0.5,
    "q": 1,
    "e": 2,
    "s": 4,
    "t": 8,
    "0": 0.0,
}

NOTES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']

ACCIDENTALS = {
    'Db': 'C#',
    'D#': 'Eb',
    'E#': 'F',
    'Gb': 'F#',
    'G#': 'Ab',
    'A#': 'Bb',
    'B#': 'C',
}

# MIDI has a bit more than 10 octaves, but we will cap at 10
OCTAVES = list(range(10))


def swap_accidental(note):
    return ACCIDENTALS.get(note, note)


def note_to_midi_int(note: str, octave: int) -> int:
    note = swap_accidental(note)
    note_int: int = NOTES.index(note)
    note_int += (len(NOTES) * octave)
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


def note_type_to_offset(duration: float, note_type: str) -> float:
    """Calculate the offset of a note at a duration."""
    duration = float(duration * NOTE_TYPE_TO_DURATION[note_type])
    return duration


