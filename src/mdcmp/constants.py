"""
Constants go here.
"""
################################################################################
# These are the supported MDC format versions:
KNOWN_MDC_FORMAT_VERSIONS = (1,)
################################################################################
# Note mappings for translating note names to MIDI timings
NOTE_TIME_MAP = {
    "W": 8,
    "w.": 6,
    "w": 4,
    "h.": 3,
    "h": 2,
    "q.": 1.5,
    "q": 1,
    "e.": 0.525,
    "e": 0.5,
    "s.": 0.375,
    "s": 0.25,
    "t.": 0.1875,
    "t": 0.125,
    "S": 0.0625,
    "H": 0.0625 / 2,
    "0": 0.0,
    "n": 0.0,
}
# for calculating note types to duration in duration (e.g. for loop range)
NOTE_TYPE_GRID_QUANTIZE_MAP = {
    "w": 0.25,
    "h": 0.5,
    "q": 1,
    "e": 2,
    "s": 4,
    "t": 8,
    "0": 0.0,
    "n": 0.0,
}
DURATION_GRANULARITY_MAP = {
    # granularity: {duration: note, ...}
    "h": {1: "h", 2: "w", 3: "w.", 4: "W"},
    "q": {1: "q", 2: "h", 3: "h.", 4: "w", 5: "w.", 6: "W"},
    "e": {1: "e", 2: "q", 3: "q.", 4: "h", 5: "h.", 6: "w", 7: "w.", 8: "W"},
    "s": {
        1: "s",
        2: "e",
        3: "e.",
        4: "q",
        5: "q.",
        6: "h",
        7: "h.",
        8: "w",
        9: "w.",
        10: "W",
    },
    "t": {
        1: "t",
        2: "s",
        3: "s.",
        4: "e",
        5: "e.",
        6: "q",
        7: "q.",
        8: "h",
        9: "h.",
        10: "w",
        11: "w.",
        12: "W",
    },
}

################################################################################
# Notes and accidentals
NOTES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

ACCIDENTALS = {
    "Db": "C#",
    "D#": "Eb",
    "E#": "F",
    "Gb": "F#",
    "G#": "Ab",
    "A#": "Bb",
    "B#": "C",
}
################################################################################
# MIDI stuff
# MIDI has a bit more than 10 octaves, but we will cap at 10
OCTAVES = list(range(11))

# Event keys for addControllerEvent()
EVENT_MODWHEEL = 1
EVENT_VOLUME = 7
EVENT_PAN = 10
EVENT_EXPRESSION = 11
EVENT_SUSTAIN = 64
# Map these values out for easy access
EVENT_MAP = {
    "volume": EVENT_VOLUME,
    "pitchwheel": None,  # This is a separate function call
    "modwheel": EVENT_MODWHEEL,
    "expression": EVENT_EXPRESSION,
    "sustain": EVENT_SUSTAIN,
    "pan": EVENT_PAN,
}

# min/max of MIDI volume integer values
VELOCITY_RANGE = list(range(0, 128))
MODWHEEL_RANGE = list(range(0, 128))
EXPRESSION_RANGE = list(range(0, 128))
VOLUME_RANGE = list(range(0, 128))
# humanized values -64 to 64 for easier control, instead of 0-N values
PAN_RANGE = list(range(-64, 65))
PITCHWHEEL_RANGE = list(range(-64, 65))
