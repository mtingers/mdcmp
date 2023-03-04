class DrumLineError(Exception):
    """Could not parse a beats line"""


class DrumFormatError(Exception):
    """Could not parse beats data section"""


class DrumNotFoundError(Exception):
    """Unknown drum"""


class MdcInvalidNoteError(Exception):
    """Unknown note"""


class MdcLineError(Exception):
    """Could not parse a composition line"""


class MdcAlignmentError(Exception):
    """The data section lists did not match the length of pitches list"""


class MdcUnknownVersionrror(Exception):
    """The header contained an unsupported version"""


class MdcFormatError(Exception):
    """Could not parse composition data section"""


class MdcInvalidGranularityError(Exception):
    """Unknown granularity size"""


class PitchNotFoundError(Exception):
    """Unknown pitch"""
