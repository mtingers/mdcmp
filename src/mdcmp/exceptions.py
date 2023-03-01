class BeatsLineError(Exception):
    """Could not parse a beats line"""


class BeatsFormatError(Exception):
    """Could not parse beats data section"""


class DrumNotFoundError(Exception):
    """Unknown drum"""


class InvalidNoteError(Exception):
    """Unknown note"""


class ComposerLineError(Exception):
    """Could not parse a composition line"""


class ComposerFormatError(Exception):
    """Could not parse composition data section"""


class PitchNotFoundError(Exception):
    """Unknown pitch"""
