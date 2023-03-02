"""
The goal of Grid() is to provide an easy way to generate and layer tracks of different types, then
produce an MCD data file for processing.

Key features:
    - Layer multiple notes at one bar beat
    - Layer multiple tracks at one bar beat
    - Control multiple tracks at the same point in time

Important notes:
    - If bars 1,2 and 5 are created, the generated output will be a full rest/blank bar for bar 3-4.
    - Notes are either classified as "drum" or "pitch".
    - Note classification checks if value matches a drum name and uses the drum.  Otherwise, it will
      attempt to translate the note or chord into a series of midi pitches.

Below is a diagram of how these are layered using a drum and instrument composition:

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

    grid.chord_spread(value='Cm7', track=3, start_bar=1, start_position=1, spacer=1)
    # grid.silence(positions=[7], bars=[2], duration=2, tracks=[2,3]) # maybe?
    grid.save('/path/save.mdc')
    raw_mdc_data = grid.data()
    # maybe? grid.reshape(Granularity.SIXTEENTH)
    grid = {
        0: {                            <-- bar
            0:                          <-- track
            [                           <-- position
                {                       <-- metadata
                    'velocity': N,
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


class Granularity(Enum):
    WHOLE = 'w'
    HALF = 'h'
    QUARTER = 'q'
    EIGHTH = 'e'
    SIXTEENTH = 's'
    THIRTYSECOND = 't'


class Grid:
    def __init__(self, granularity:  Granularity = Granularity.EIGHTH):
        self.granularity: str = granularity.value
        self.number_of_positions: int = int(NOTE_TYPE_TO_DURATION[self.granularity] * 4)
        # self.grid: dict[int, dict[int, dict[str, Any]]] = {}
        self.grid: dict[int, dict[int, list[list[dict[str, Any]]]]] = {}
        print('DEBUG:', self.granularity, self.number_of_positions)

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
            raise Exception('Both bars and tracks must be specified.')
        next_bar_index = max(list(self.grid.keys())) + 1
        for bar in bars:
            tmp = self.grid.get(bar, None)
            if not tmp:
                raise Exception(f'invalid bar specified: {bar}')
            for track in tracks:
                track_tmp = tmp.get(track, None)
                if not track_tmp:
                    raise Exception(f'invalid track specified: {track}')
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
                    for position, data in enumerate(track_tmp):
                        for d in data:
                            self.add(
                                bars=[next_bar_index], tracks=[track], positions=[position],
                                value=d['value'], duration=d['duration'],
                                velocity=d['velocity']
                            )
                next_bar_index += 1

    def add(
        self,
        bars: list[int] | None = None,
        tracks: list[int] | None = None,
        positions: list[int] | None = None,
        value: str = '',
        duration: int = 1,
        velocity: int = 50,
    ):
        if not bars or not tracks or not positions:
            raise Exception("All parameters must be set")

        for bar in bars:
            if bar not in self.grid:
                self.grid[bar] = {}
            for track in tracks:
                if track not in self.grid[bar]:
                    self.grid[bar][track] = []
                    for _ in range(self.number_of_positions):
                        self.grid[bar][track].append([])
                    print("LEN:", len(self.grid[bar][track]))
                for position in positions:
                    if position >= len(self.grid[bar][track]):
                        raise Exception((
                            "Position is greater than the grids granularity size: "
                            f"{position} >= {len(self.grid[bar][track])}"
                        ))
                    # -1 is a wildcard for fill all positions
                    if position == -1:
                        for wildcard in range(self.number_of_positions):
                            self.grid[bar][track][wildcard].append({
                                'velocity': velocity, 'duration': duration, 'value': value
                            })
                    else:
                        self.grid[bar][track][position].append({
                            'velocity': velocity, 'duration': duration, 'value': value
                        })

    def to_data(self, velocity_jitter: int = 5) -> str:
        return ''

    def save(self, path: str, velocity_jitter: int = 5):
        with open(path, "w") as outfd:
            outfd.write(self.to_data(velocity_jitter=velocity_jitter))

    def dump_grid(self):
        from pprint import pprint
        pprint(self.grid, width=120)
