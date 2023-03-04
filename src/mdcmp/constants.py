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
OCTAVES = list(range(10))
# min/max of MIDI volume integer values
VOLUME_MIN = 0
VOLUME_MAX = 127
VOLUME_RANGE = (0, 127)
