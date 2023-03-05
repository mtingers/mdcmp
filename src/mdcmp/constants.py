"""
Constants go here.
"""
################################################################################
# These are the supported MDC format versions:
KNOWN_MDC_FORMAT_VERSIONS = (1,)
################################################################################
# Note mappings for translating note names to MIDI timings
NOTE_TIME_MAP = {
    "w": 4,
    "h": 2,
    "q": 1,
    "e": 0.5,
    "s": 0.25,
    "t": 0.125,
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
    'volume': EVENT_VOLUME,
    'pitchwheel': None,  # This is a separate function call
    'modwheel': EVENT_MODWHEEL,
    'expression': EVENT_EXPRESSION,
    'sustain': EVENT_SUSTAIN,
    'pan': EVENT_PAN,
}

# min/max of MIDI volume integer values
VELOCITY_RANGE = list(range(0, 128))
MODWHEEL_RANGE = list(range(0, 128))
EXPRESSION_RANGE = list(range(0, 128))
VOLUME_RANGE = list(range(0, 128))
# humanized values -64 to 64 for easier control, instead of 0-N values
PAN_RANGE = list(range(-64, 65))
PITCHWHEEL_RANGE = list(range(-64, 65))
