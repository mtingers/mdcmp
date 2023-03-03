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
    grid.save('/path/save.mdc')
    raw_mdc_data = grid.data()
    # maybe add resphape() grid.reshape(Granularity.SIXTEENTH)
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
import random
from .drummap import DRUMS_R
from .util import NOTE_TYPE_TO_DURATION
from .util import chord_to_midi

# The wildcard pattern to specify all of something (e.g. for bars, beats, tracks)
# This is like instead of specifying [1,2,3] you can do a '*' glob to specify all.
WILDCARD = -1

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


class IsChord(Enum):
    NO = 0
    YES = 1
    PRESERVE = -1


class Granularity(Enum):
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
        self.grid: dict[int, dict[int, list[list[dict[str, Any]]]]] = {}

    def copy_to_end(
        self,
        bars: list[int] | None = None,
        tracks: list[int] | None = None,
        count: int = 1,
    ):
        """
        Copy bars and append to the end, in order, count times, for the tracks specified.
        """
        if not bars or not tracks:
            raise RequiredArgsGridError(
                "Both bars and tracks parameters must be specified."
            )
        next_bar_index = max(list(self.grid.keys())) + 1
        # Now copy each bar->track to a new bar at the end
        for _ in range(count):
            for bar in bars:
                tmp = self.grid.get(bar)
                if not tmp:  # silence pyright None check
                    raise BarIndexGridError(f"Invalid bar index specified: {bar}")
                for track in tracks:
                    track_tmp = tmp.get(track)
                    if not track_tmp:
                        raise TrackIndexGridError(
                            f"Invalid track index specified: {track}"
                        )
                    for beat, data in enumerate(track_tmp):
                        for d in data:
                            self.add(
                                bars=[next_bar_index],
                                tracks=[track],
                                beats=[beat],
                                value=d["value"],
                                duration=d["duration"],
                                volume=d["volume"],
                                is_chord=d["is_chord"],
                            )
                next_bar_index += 1

    def add(
        self,
        bars: list[int] | None = None,
        tracks: list[int] | None = None,
        beats: list[int] | None = None,
        value: str = "",
        # duration lists set each beat duration.
        duration: int | list[int] = 1,
        volume: int = 50,
        octave: int = 3,
        is_chord: IsChord = IsChord.NO,
    ):
        if not bars or not tracks or not beats:
            raise RequiredArgsGridError(
                "bars, tracks, and beats arguments must be set."
            )
        if WILDCARD in bars:
            bars = list(self.grid.keys())
        for bar in bars:
            if bar not in self.grid:
                self.grid[bar] = {}
            if WILDCARD in tracks:
                tracks = list(self.grid[bar].keys())
            for track in tracks:
                if track not in self.grid[bar]:
                    self.grid[bar][track] = []
                    for _ in range(self.number_of_beats):
                        self.grid[bar][track].append([])
                for beat_n, beat in enumerate(beats):
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
                            if isinstance(duration, list):
                                duration_tmp = duration[wildcard]
                            else:
                                duration_tmp = duration
                            self.grid[bar][track][wildcard].append(
                                {
                                    "volume": volume,
                                    "octave": octave,
                                    "duration": duration_tmp,
                                    "value": value,
                                    "is_chord": is_chord,
                                }
                            )
                    else:
                        if isinstance(duration, list):
                            print(beat, duration)
                            duration_tmp = duration[beat_n]
                        else:
                            duration_tmp = duration
                        self.grid[bar][track][beat].append(
                            {
                                "volume": volume,
                                "octave": octave,
                                "duration": duration_tmp,
                                "value": value,
                                "is_chord": is_chord,
                            }
                        )

    def transform(
        self,
        bars: list[int] | None = None,
        tracks: list[int] | None = None,
        beats: list[int] | None = None,
        duration: int | list[int] | None = None,
        volume: int = 50,
        octave: int = -1,
        is_chord: IsChord = IsChord.PRESERVE,
    ):
        """
        Adjust the volume, duration, is_chord of the specified items
        """
        # grid.silence(beats=[7], bars=[2], duration=2, tracks=[2,3]) # maybe?
        if not bars or not tracks or not beats:
            raise RequiredArgsGridError("All args must have a value.")
        # Now copy each bar->track to a new bar at the end
        if WILDCARD in bars:
            bars = list(self.grid.keys())
        if WILDCARD in beats:
            beats = list(range(self.number_of_beats))
        for bar in bars:
            if WILDCARD in tracks:
                tracks_list = list(self.grid[bar].keys())
            else:
                tracks_list = tracks
            for track in tracks_list:
                for beat in beats:
                    for i, _ in enumerate(self.grid[bar][track][beat]):
                        if isinstance(duration, list):
                            duration_tmp = duration[i]
                        else:
                            duration_tmp = duration
                        if octave >= 0:
                            self.grid[bar][track][beat][i]["octave"] = octave
                        if duration_tmp:
                            self.grid[bar][track][beat][i]["duration"] = duration_tmp
                        self.grid[bar][track][beat][i]["volume"] = volume
                        self.grid[bar][track][beat][i]["is_chord"] = is_chord

    def fill_gaps(self):
        """Insert empty bars where gaps exist"""
        bars_list = sorted(list(self.grid.keys()))
        for n, i in enumerate(bars_list):
            if n < i:
                # Missing bar n or more, insert them
                for x in range(n, i):
                    if x not in self.grid:
                        self.add(bars=[x], tracks=[WILDCARD], beats=[WILDCARD])
        bars_list = sorted(list(self.grid.keys()))
        tracks_list = set()
        for bar in bars_list:
            for track in self.grid[bar].keys():
                tracks_list.add(track)
        for track in tracks_list:
            for bar in bars_list:
                if track not in self.grid[bar]:
                    print("ADD:", bar, track)
                    self.grid[bar][track] = []

    def to_data(self, volume_jitter: int = 5, humanize_jitter: bool = False) -> str:
        """Convert grid to MDC format data

        Args:
            volume_jitter (int): Randomly volume adjust +-volume_jitter
            humanize_jitter (int): Randomly humanize note timings +-humanize_jitter
        Return:
            str: MDC data
        """
        # 1) Ensure all bars exist and there are no gaps
        self.fill_gaps()

        # 2) Create MDC data form the grid forced to the grid granularity.
        #    This will fill in gaps where necessary (e.g. with rests), to keep alignment.
        bars_list = sorted(list(self.grid.keys()))
        tracks_list = set()
        for bar in bars_list:
            for track in self.grid[bar].keys():
                tracks_list.add(track)
        result: dict[int, dict[str, str]] = {}
        for bar in self.grid.keys():
            for track in tracks_list:
                if track not in result:
                    result[track] = {"meta": "", "data": ""}
                # If the track doesn't exist in this bar, create resting space, zeroed out
                if track not in self.grid[bar]:
                    for _ in range(self.number_of_beats):
                        result[track]["data"] += f" 0,{self.granularity},n,0;"
                else:
                    for beat in range(self.number_of_beats):
                        pitches = []
                        notes = []
                        offsets = []
                        volumes = []
                        # collect pitches, collect notes, collect offsets, collect volumes
                        if not self.grid[bar][track]:
                            # add rest beat to keep timing alignment
                            result[track]["data"] += f" 0,{self.granularity},n,0;"
                            continue
                        if not self.grid[bar][track][beat]:
                            # add rest beat to keep timing alignment
                            result[track]["data"] += f" 0,{self.granularity},n,0;"
                            continue

                        for _, j in enumerate(self.grid[bar][track][beat]):
                            # convert to drum or chord or single pitch
                            if j["value"] in DRUMS_R:
                                pitches.append(DRUMS_R[j["value"]])
                                result[track][
                                    "meta"
                                ] = f"_|drum|{self.granularity}|0.0|"
                            else:
                                result[track][
                                    "meta"
                                ] = f"_|instrument|{self.granularity}|0.0|"
                                pitch = chord_to_midi(j["value"], j["octave"])
                                if not j["is_chord"]:
                                    pitches.append(pitch[0])
                                else:
                                    for p in pitch:
                                        pitches.append(p)
                            # convert duration to whqst value
                            # duration = 1, granularity = e
                            # 1 = e -> e
                            # 2 = e -> q
                            # 3 = e -> q.
                            # 4 = e -> h
                            # 5 = e -> h.
                            duration_tmp = DURATION_GRANULARITY_MAP[self.granularity][
                                j["duration"]
                            ]
                            notes.append(duration_tmp)
                            if humanize_jitter:
                                offsets.append(
                                    random.choice("nnnnt")
                                )  # TODO: not implemented yet
                            else:
                                offsets.append("n")
                            jitter = random.randint(-volume_jitter, volume_jitter)
                            new_volume = j["volume"] + jitter
                            if new_volume < 0:
                                new_volume = j["volume"]
                            volumes.append(new_volume)
                        # Now join all of these lists into MDC format lists
                        result[track]["data"] += (
                            f" {'!'.join(map(str, pitches))},"
                            f"{'!'.join(map(str, notes))},"
                            f"{'!'.join(map(str, offsets))},"
                            f"{'!'.join(map(str, volumes))};"
                        )
        output: str = "1\n"
        for i in result.values():
            output += f"{i['meta']}{i['data']}\n"
        import pprint

        pprint.pprint(result)
        return output

    def save(self, path: str, volume_jitter: int = 5, humanize_jitter: bool = False):
        """Generate MDC format data and save to path"""
        with open(path, "w") as outfd:
            outfd.write(
                self.to_data(
                    volume_jitter=volume_jitter, humanize_jitter=humanize_jitter
                )
            )

    def dump_grid(self):
        """Pretty print the grid data"""
        from pprint import pprint

        pprint(self.grid, width=100)
