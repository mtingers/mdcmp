"""
The goal of Grid() is to provide an easy way to generate and layer tracks of different types, then
produce an MCD data file for processing.

Key features:
    - Layer multiple notes at one bar beat.
    - Layer multiple tracks on top of each other.
    - Easily copy and repeat bars.
    - Run mass transformation on groups of bars and tracks.

Notes:
    - If bars 1,2 and 5 are created, the generated output will be a full rest/blank bar for bar 3-4.
    - Notes are either classified as "drum" or "instrument".
    - Note classification checks if value matches a drum name and uses the drum.  Otherwise, it will
      attempt to translate the note or chord into a series of midi pitches when generating the MDC
      data file.

Granularity:
When a grid is initially defined, it has a set granularity related to a type of note (e.g. half,
quarter, eighth, sixteenth, or thirtysecond).  A bar will have N beats based off of this
granularity.  For example, a granularity of half note only has 2 beats per bar, where a granularity
of quarter note has 4, and eighth has 8 beats, etc.

TODO:
    - Spread a chord across beats:
        grid.chord_spread(value='Cm7', track=3, start_bar=1, start_beat=1, spacer=1)
    - Maybe add resphape(), but this could be difficult:
        grid.reshape(new_granularity=Granularity.SIXTEENTH)


Below is a diagram of how these are layered using a drum and instrument composition:


    track-1:               bar-1            bar-2
    track-1:      +-----------------------------------+
    track-1:  time| 0 1 2 3 4 5 6 7 | 0 1 2 3 4 5 6 7 |
    track-1:      +-----------------------------------+
    track-1:  kick| k       k       | k       k       |
    track-1: snare|     s       s   |     s       s   |
    track-1:   hat| h h h h h h h h | h h h h h h h h |
    track-1:      +-----------------------------------+
    ===================================================
    track-2:               bar-1            bar-2
    track-2:      +-----------------------------------+
    track-2:  time| 0 1 2 3 4 5 6 7 | 0 1 2 3 4 5 6 7 |
    track-2:      +-----------------------------------+
    track-2:      | C               |                 |
    track-2:      | Eb  Eb          |     Eb          |
    track-2:      | G               |                 |
    track-2:      | Bb              |                 |
    track-2:      +-----------------------------------+

---------------------------------------------------------------------------------------------------
TODO: Implement the following automation controller.  Right now it is grouped with the track data,
but this causes issues if multiple calls to the same bar:track:beat are called. It currently
takes the last call's event and ignores the others. Example:

    # This will take the last volume value "50" and is confusing since it seems like hat1/snare1
    # have an independent volume, but it is the entire volume of the track:
    grid.add(bars=[1,], tracks=[0,], beats=[1], value="hat1", duration=1, volume=100)
    grid.add(bars=[1,], tracks=[0,], beats=[1], value="snare1", duration=1, volume=50)

TODO:
And each track is assigned an automation controller to change the entire track settings for volume,
pan, modwheel, pitchwheel, expression, and sustain.  Example:

    controller:                    bar-1            bar-2
    controller:           +-----------------------------------+
    controller:       time| 0 1 2 3 4 5 6 7 | 0 1 2 3 4 5 6 7 |
    controller:           +-----------------------------------+
    controller:        pan| 5   0   -5      | -9              | -64 - +64
    controller: pitchwheel|                 |                 | -64 - +64
    controller:     volume|                 |                 | 0 - 127
    controller:   modwheel|                 |                 | 0 - 127
    controller: expression|                 |                 | 0 - 127
    controller:    sustain| y               | n               | 0=off, >=64=on
    controller:           +-----------------------------------+
---------------------------------------------------------------------------------------------------

Grid datastructure:
    grid = {
        0: {                            <-- bar
            0:                          <-- track
            [                           <-- beat
                {                       <-- metadata
                    'velocity': N,
                    'duration': N,
                    'value': 'X',
                    ...
                }
            ],
        }
    }
"""
from enum import Enum
from typing import Any
import random
from .drummap import DRUMS_R
from .util import NOTE_TYPE_GRID_QUANTIZE_MAP
from .util import chord_to_midi, sustain_toggle, event_translate, pan_to_midi, pitchwheel_to_midi

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


def _compress_mdc_part(items: list, entire_track_event: bool = False) -> str:
    tmp = list(map(str, items))
    if len(set(tmp)) < 2:
        return '!'.join(set(tmp))
    # If this applies to the entire track, filter out "n" values and flatten into only 1 value
    if entire_track_event:
        return list(filter(lambda x: (x != "n"), tmp))[-1]
    return '!'.join(tmp)


class Grid:
    def __init__(self, granularity: Granularity = Granularity.EIGHTH, beats_per_measure: int = 4):
        self.granularity: str = granularity.value
        self.number_of_beats: int = int(
            NOTE_TYPE_GRID_QUANTIZE_MAP[self.granularity] * beats_per_measure
        )
        self.grid: dict[int, dict[int, list[list[dict[str, Any]]]]] = {}
        if beats_per_measure != 4:
            raise ValueError("Not implemented. This program currently only support 4/4 time.")

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
                                expression=d["expression"],
                                is_chord=d["is_chord"],
                                modwheel=d["modwheel"],
                                octave=d["octave"],
                                pan=d["pan"],
                                pitchwheel=d["pitchwheel"],
                                sustain=d["sustain"],
                                velocity=d["velocity"],
                                volume=d["volume"],
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
        velocity: int = 50,
        octave: int = 3,
        volume: int | None = None,
        pitchwheel: int | None = None,
        modwheel: int | None = None,
        expression: int | None = None,
        pan: int | None = None,
        sustain: bool | None = None,
        is_chord: IsChord = IsChord.NO,
    ):
        """
        Add grid item(s).

        Args:
            bars (list[int] | None): ...
            tracks (list[int] | None): ...
            beats (list[int] | None): ...
            value (str): ...
            duration (list[int] | None,  default 1): ...
            velocity (int, default 50): ...
            octave (int, default 3)
            volume (int | None): ...
            pitchwheel (int | None): ...
            modwheel (int | None): ...
            expression (int | None): ...
            pan (int | None): ...
            sustain (int | None): ...
            is_chord (IsChord enum): ...

        TODO: Validation, see constants *_RANGE values.
        """
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
                                    "duration": duration_tmp,
                                    "expression": expression,
                                    "is_chord": is_chord,
                                    "modwheel": modwheel,
                                    "octave": octave,
                                    "pan": pan,
                                    "pitchwheel": pitchwheel,
                                    "sustain": sustain,
                                    "value": value,
                                    "velocity": velocity,
                                    "volume": volume,
                                }
                            )
                    else:
                        if isinstance(duration, list):
                            duration_tmp = duration[beat_n]
                        else:
                            duration_tmp = duration
                        self.grid[bar][track][beat].append(
                            {
                                "duration": duration_tmp,
                                "expression": expression,
                                "is_chord": is_chord,
                                "modwheel": modwheel,
                                "octave": octave,
                                "pan": pan,
                                "pitchwheel": pitchwheel,
                                "sustain": sustain,
                                "value": value,
                                "velocity": velocity,
                                "volume": volume,
                            }
                        )

    def transform(
        self,
        bars: list[int] | None = None,
        tracks: list[int] | None = None,
        beats: list[int] | None = None,
        duration: int | list[int] | None = None,
        velocity: int = 50,
        octave: int = -1,
        volume: int | None = None,
        pitchwheel: int | None = None,
        modwheel: int | None = None,
        expression: int | None = None,
        pan: int | None = None,
        sustain: bool | None = None,
        is_chord: IsChord = IsChord.PRESERVE,
    ):
        """
        Adjust the velocity, duration, is_chord of the specified items
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
                        self.grid[bar][track][beat][i]["velocity"] = velocity
                        self.grid[bar][track][beat][i]["is_chord"] = is_chord
                        self.grid[bar][track][beat][i]["volume"] = volume
                        self.grid[bar][track][beat][i]["pitchwheel"] = pitchwheel
                        self.grid[bar][track][beat][i]["modwheel"] = modwheel
                        self.grid[bar][track][beat][i]["expression"] = expression
                        self.grid[bar][track][beat][i]["pan"] = pan
                        self.grid[bar][track][beat][i]["sustain"] = sustain

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
                    self.grid[bar][track] = []

    def to_data(self, velocity_jitter: int = 5, humanize_jitter: bool = False) -> str:
        """Convert grid to MDC format data

        Args:
            velocity_jitter (int): Randomly velocity adjust +-velocity_jitter
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
                        result[track]["data"] += f" 0,{self.granularity},n,0,n,n,n,n,n,n,n;"
                else:
                    for beat in range(self.number_of_beats):
                        pitches = []
                        notes = []
                        offsets = []
                        velocities = []
                        volumes = []
                        pitchwheels = []
                        modwheels = []
                        expressions = []
                        sustains = []
                        pans = []
                        # collect pitches, collect notes, collect offsets, collect velocities
                        if not self.grid[bar][track]:
                            # add rest beat to keep timing alignment
                            result[track]["data"] += f" 0,{self.granularity},n,0,n,n,n,n,n,n;"
                            continue
                        if not self.grid[bar][track][beat]:
                            # add rest beat to keep timing alignment
                            result[track]["data"] += f" 0,{self.granularity},n,0,n,n,n,n,n,n;"
                            continue

                        # self.grid[bar][track][beat][i]["sustain"] = sustain
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
                                if j["is_chord"] == IsChord.NO:
                                    pitches.append(pitch[0])
                                else:
                                    for p in pitch:
                                        pitches.append(p)
                            duration_tmp = DURATION_GRANULARITY_MAP[self.granularity][
                                j["duration"]
                            ]
                            notes.append(duration_tmp)
                            if humanize_jitter:
                                offsets.append(
                                    random.choice(["n", "n", "n", "n", "n", "H", "H", "H", "S"])
                                )
                            else:
                                offsets.append("n")
                            jitter = random.randint(-velocity_jitter, velocity_jitter)
                            new_velocity = j["velocity"] + jitter
                            if new_velocity < 0:
                                new_velocity = j["velocity"]
                            velocities.append(new_velocity)
                            volumes.append(event_translate(j["volume"]))
                            pitchwheels.append(
                                event_translate(pitchwheel_to_midi(j["pitchwheel"]))
                            )
                            modwheels.append(event_translate(j["modwheel"]))
                            expressions.append(event_translate(j["expression"]))
                            sustains.append(sustain_toggle(j["sustain"]))
                            pans.append(
                                event_translate(pan_to_midi(j["pan"]))
                            )
                        # Now join all of these lists into MDC format lists
                        # Maybe set these in a wrapper to compress if all are the same.?
                        result[track]["data"] += (
                            f" {_compress_mdc_part(pitches)},"
                            f"{_compress_mdc_part(notes)},"
                            f"{_compress_mdc_part(offsets)},"
                            f"{_compress_mdc_part(velocities)},"
                            f"{_compress_mdc_part(volumes, entire_track_event=True)},"
                            f"{_compress_mdc_part(pitchwheels, entire_track_event=True)},"
                            f"{_compress_mdc_part(modwheels, entire_track_event=True)},"
                            f"{_compress_mdc_part(expressions, entire_track_event=True)},"
                            f"{_compress_mdc_part(sustains, entire_track_event=True)},"
                            f"{_compress_mdc_part(pans, entire_track_event=True)};"
                        )
        output: str = "1\n"
        for i in result.values():
            output += f"{i['meta']}{i['data']}\n"
        import pprint

        pprint.pprint(result)
        return output

    def save(self, path: str, velocity_jitter: int = 5, humanize_jitter: bool = False):
        """Generate MDC format data and save to path"""
        with open(path, "w") as outfd:
            outfd.write(
                self.to_data(
                    velocity_jitter=velocity_jitter, humanize_jitter=humanize_jitter
                )
            )

    def dump_grid(self):
        """Pretty print the grid data"""
        from pprint import pprint

        pprint(self.grid, width=100)
