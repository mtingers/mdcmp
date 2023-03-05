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


def pitchwheel_to_midi(simple_value: int | None) -> int | None:
    """Normalize pitch wheel values from -64 to 64 and convert to midi value"""
    if simple_value is None:
        return None
    x: int = simple_value
    if x > 64 or x < -64:
        raise ValueError("simple_value must be between -64 and 64")
    if x < 0 and x != 64:
        return 128 * x
    return (128 * x) - 1


def pan_to_midi(simple_value: int | None) -> int | None:
    """Normalize pan values from -64 to 64 and convert to midi value"""
    if simple_value is None:
        return None
    x: int = simple_value
    if x < -64 or x > 64:
        raise ValueError("x must be between -64 and 64")
    if x < 0 or x != 64:
        return 64 + x
    return (64 + x) - 1


def sustain_toggle(value: bool | None) -> str:
    """Sustain is either on or off. <64=off"""
    if value is None:
        return "n"
    if value:
        return "64"
    return "0"


def event_translate(value: int | None) -> str:
    if value is None:
        return "n"
    return str(value)
