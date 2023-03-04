from mingus.core import chords
from .constants import ACCIDENTALS, NOTES, NOTE_TYPE_GRID_QUANTIZE_MAP


def swap_accidental(note):
    return ACCIDENTALS.get(note, note)


def note_to_midi_int(note: str, octave: int) -> int:
    """Convert a note to MIDI pitch value"""
    note = swap_accidental(note)
    note_int: int = NOTES.index(note)
    note_int += len(NOTES) * octave
    return note_int


def progression_to_midi(chord_progression: list[str], octave: int) -> list[int]:
    """Convert a chord progression to MIDI pitch values"""
    notes = []
    note_numbers = []
    for chord in chord_progression:
        notes.extend(chords.from_shorthand(chord))
    for note in notes:
        note_numbers.append(note_to_midi_int(note, octave))
    return note_numbers


def chord_to_midi(chord: str, octave: int) -> list[int]:
    """Convert a chord to MIDI pitch values"""
    notes: list[str] = chords.from_shorthand(chord)
    midi_notes: list[int] = []
    for note in notes:
        midi_notes.append(note_to_midi_int(note, octave))
    return midi_notes


def note_type_to_offset(duration: float, note_type: str) -> float:
    """Calculate the offset of a note at a duration."""
    duration = float(duration * NOTE_TYPE_GRID_QUANTIZE_MAP[note_type])
    return duration
