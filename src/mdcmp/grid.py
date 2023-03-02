"""
The goal of Grid() is to provide an easy way to generate and layer tracks of different types, then
produce  an MCD data file for processing.

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

    grid = Grid(quantize='e')
    grid.drum(positions=[1,5], bars=[1,2], value='kick1', track=1, duration=2, velocity=50)
    grid.drum(positions=[3,7], bars=[1,2], value='snare1', track=1, duration=2, velocity=50)
    grid.drum(positions=[0], bars=[1,2], value='hat1', track=1, duration=1, velocity=50)
    grid.chord(positions=[1], bars=[1], value='Cm7', track=2, duration=2, velocity=50)
    grid.chord(positions=[1], bars=[1], value='Cm7', track=2, duration=2, velocity=50)
    grid.note(positions=[3], bars=[1,2], value='Eb', track=2, duration=2, velocity=50)
    grid.chord_spread(value='Cm7', track=3, start_bar=1, start_position=1, spacer=1)
    # grid.silence(positions=[7], bars=[2], duration=2, tracks=[2,3]) # maybe?
    # grid.extend(nbars=2)  # add 2 more blank bars, don't need this since compiling the output
      will fill in missing bars as blank
    grid.copy_to_end(bars=[2,1], count=2, tracks=[1,2])  # copy bars 2+1 (in that order) to the
      end 2 times, but add blank bars for track3
    grid.save('/path/save.mdc')
    raw_mdc_data = grid.data()
    # maybe? grid.reshape(Quantize.SIXTEENTH)
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


class Quantize(Enum):
    WHOLE = 'w'
    HALF = 'h'
    QUARTER = 'q'
    EIGHTH = 'e'
    SIXTEENTH = 's'
    THIRTYSECOND = 't'


class Grid:
    def __init__(self, quantize:  Quantize = Quantize.EIGHTH):
        self.quantize: str = quantize.value
        self.number_of_positions: int = NOTE_TYPE_TO_DURATION[self.quantize] * 4
        # self.grid: dict[int, dict[int, dict[str, Any]]] = {}
        self.grid: dict[int, dict[int, list[dict[str, Any]]]] = {}

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
                        self._add_to_grid(
                            bars=[next_bar_index], tracks=tracks, positions=[position],
                            value=data['value'], duration=data['duration'],
                            velocity=data['velocity']
                        )
                next_bar_index += 1

    def drum(
        self,
        bars: list[int] | None = None,
        tracks: list[int] | None = None,
        positions: list[int] | None = None,
        value: str = '',
        duration: int = 1,
        velocity: int = 50,
    ):
        self._add_to_grid(
            bars=bars, tracks=tracks, positions=positions,
            value=value, duration=duration, velocity=velocity
        )

    def note(
        self,
        bars: list[int] | None = None,
        tracks: list[int] | None = None,
        positions: list[int] | None = None,
        value: str = '',
        duration: int = 1,
        velocity: int = 50,
    ):
        self._add_to_grid(
            bars=bars, tracks=tracks, positions=positions,
            value=value, duration=duration, velocity=velocity
        )

    def chord(
        self,
        bars: list[int] | None = None,
        tracks: list[int] | None = None,
        positions: list[int] | None = None,
        value: str = '',
        duration: int = 1,
        velocity: int = 50,
    ):
        self._add_to_grid(
            bars=bars, tracks=tracks, positions=positions,
            value=value, duration=duration, velocity=velocity
        )

    def _add_to_grid(
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
                        self.grid[bar][track].append({})
                for position in positions:
                    self.grid[bar][track][position] = {
                        'velocity': velocity, 'duration': duration, 'value': value
                    }
