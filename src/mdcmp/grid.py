"""
The goal of Grid() is to provide an easy way to generate and layer tracks of different types, then
produce an MCD data file for processing.

Key features:
    - Layer multiple notes at one bar beat.
    - Layer multiple tracks on top of each other.
    - Easily copy and repeat bars.

Notes:
    - If bars 1,2 and 5 are created, the generated output will be a full rest/blank bar for bar 3-4.
    - Notes are either classified as "drum" or "pitch".
    - Note classification checks if value matches a drum name and uses the drum.  Otherwise, it will
      attempt to translate the note or chord into a series of midi pitches when generating the MDC
      data file.

Granularity notes:
When a grid is initially defined, it has a set granularity related to a type of note (e.g. whole,
half, quarter, eighth, sixteenth, or thirtysecond).  A bar will have N beats based off of this
granularity.  For example, a granularity of whole note only has 1 beat per bar, where a granularity
of quarter note has 4, and eighth has 8 beats.


Below is a diagram of how these are layered using a drum and instrument combeat:

    #######################################################
    track-1:               bar-1            bar-2
    track-1:      +-----------------------------------+
    track-1:  time| 1 2 3 4 5 6 7 8 | 1 2 3 4 5 6 7 8 |
    track-1:      +-----------------------------------+
    track-1:  kick| k       k       | k       k       |
    track-1: snare|     s       s   |     s       s   |
    track-1:   hat| h h h h h h h h | h h h h h h h h |
    track-1:      +-----------------------------------+
    #######################################################
    track-2:               bar-1            bar-2
    track-2:      +-----------------------------------+
    track-2:  time| 1 2 3 4 5 6 7 8 | 1 2 3 4 5 6 7 8 |
    track-2:      +-----------------------------------+
    track-2:      | C               |                 |
    track-2:      | Eb  Eb          |     Eb          |
    track-2:      | G               |                 |
    track-2:      | Bb              |                 |
    track-2:      +-----------------------------------+
    #######################################################

    grid.chord_spread(value='Cm7', track=3, start_bar=1, start_beat=1, spacer=1)
    # grid.silence(beats=[7], bars=[2], duration=2, tracks=[2,3]) # maybe?
    grid.save('/path/save.mdc')
    raw_mdc_data = grid.data()
    # maybe? grid.reshape(Granularity.SIXTEENTH)
    grid = {
        0: {                            <-- bar
            0:                          <-- track
            [                           <-- beat
                {                       <-- metadata
                    'volume': N,
                    'duration': N,
                    'value': 'X',
                }
            ],
        }
    }
"""
from enum import Enum
from typing import Any
from .util import NOTE_TYPE_TO_DURATION

# The wildcard pattern
WILDCARD = -1


class Granularity(Enum):
    WHOLE = "w"
    HALF = "h"
    QUARTER = "q"
    EIGHTH = "e"
    SIXTEENTH = "s"
    THIRTYSECOND = "t"


class RequiredArgsGridError(Exception):
    """One or more required argument has a None value."""


class BarIndexGridError(Exception):
    """Invalid bar index."""


class TrackIndexGridError(Exception):
    """Invalid track index."""


class GranularityIndexGridError(Exception):
    """The specified beat was greater than the granularity of the grid."""


class Grid:
    def __init__(self, granularity: Granularity = Granularity.EIGHTH):
        self.granularity: str = granularity.value
        self.number_of_beats: int = int(NOTE_TYPE_TO_DURATION[self.granularity] * 4)
        # self.grid: dict[int, dict[int, dict[str, Any]]] = {}
        self.grid: dict[int, dict[int, list[list[dict[str, Any]]]]] = {}

    def copy_to_end(
        self,
        bars: list[int] | None = None,
        tracks: list[int] | None = None,
        count: int = 1,
    ):
        """
        Copy bars and append to the end, in order, count times, for the tracks specified.
        This one is a doozy.
        """
        if not bars or not tracks:
            raise RequiredArgsGridError("Both bars and tracks parameters must be specified.")
        next_bar_index = max(list(self.grid.keys())) + 1
        for bar in bars:
            tmp = self.grid.get(bar, None)
            if not tmp:
                raise BarIndexGridError(f"Invalid bar index specified: {bar}")
            for track in tracks:
                track_tmp = tmp.get(track, None)
                if not track_tmp:
                    raise TrackIndexGridError(f"Invalid track index specified: {track}")
        # Now copy each bar->track to a new bar at the end
        for _ in range(count):
            for bar in bars:
                tmp = self.grid.get(bar)
                if not tmp:  # silence pyright None check
                    continue
                for track in tracks:
                    track_tmp = tmp.get(track)
                    if not track_tmp:
                        continue
                    for beat, data in enumerate(track_tmp):
                        for d in data:
                            self.add(
                                bars=[next_bar_index],
                                tracks=[track],
                                beats=[beat],
                                value=d["value"],
                                duration=d["duration"],
                                volume=d["volume"],
                                single_note=d["single_note"],
                            )
                next_bar_index += 1

    def add(
        self,
        bars: list[int] | None = None,
        tracks: list[int] | None = None,
        beats: list[int] | None = None,
        value: str = "",
        duration: int = 1,
        volume: int = 50,
        single_note=False,
    ):
        if not bars or not tracks or not beats:
            raise RequiredArgsGridError("bars, tracks, and beats arguments must be set.")

        for bar in bars:
            if bar not in self.grid:
                self.grid[bar] = {}
            for track in tracks:
                if track not in self.grid[bar]:
                    self.grid[bar][track] = []
                    for _ in range(self.number_of_beats):
                        self.grid[bar][track].append([])
                for beat in beats:
                    if beat >= len(self.grid[bar][track]):
                        raise GranularityIndexGridError(
                            (
                                "Position is greater than the grids granularity size: "
                                f"{beat} >= {len(self.grid[bar][track])}"
                            )
                        )
                    # -1 is a wildcard for fill all beats
                    if beat == WILDCARD:
                        for wildcard in range(self.number_of_beats):
                            self.grid[bar][track][wildcard].append(
                                {
                                    "volume": volume,
                                    "duration": duration,
                                    "value": value,
                                    "single_note": single_note,
                                }
                            )
                    else:
                        self.grid[bar][track][beat].append(
                            {"volume": volume, "duration": duration, "value": value}
                        )

    def dampen(
        self,
        bars: list[int] | None = None,
        tracks: list[int] | None = None,
        beats: list[int] | None = None,
        duration: int = 1,
        volume: int = 50,
    ):
        """
        Adjust the volume/volume of the specified items. Note that this can completely mute with a
        volume of 0.
        """
        # grid.silence(beats=[7], bars=[2], duration=2, tracks=[2,3]) # maybe?
        if not bars or not tracks:
            raise RequiredArgsGridError("Both bars and tracks parameters must be specified.")
        for bar in bars:
            tmp = self.grid.get(bar, None)
            if not tmp:
                raise BarIndexGridError(f"Invalid bar index specified: {bar}")
            for track in tracks:
                track_tmp = tmp.get(track, None)
                if not track_tmp:
                    raise TrackIndexGridError(f"Invalid track index specified: {track}")

    def to_data(self, volume_jitter: int = 5) -> str:
        return ""

    def save(self, path: str, volume_jitter: int = 5):
        with open(path, "w") as outfd:
            outfd.write(self.to_data(volume_jitter=volume_jitter))

    def dump_grid(self):
        from pprint import pprint

        pprint(self.grid, width=120)
