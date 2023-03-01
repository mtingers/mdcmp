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


def note_to_offset(duration: float, note_type: str) -> float:
    """Calculate the offset of a note at a duration."""
    duration = float(duration * NOTE_TYPE_TO_DURATION[note_type])
    return duration
