from random import shuffle
from mdcmp.grid import Grid, Granularity, WILDCARD, IsChord
from mdcmp.converter import Converter
from mingus.core import chords


def chord_spread(
        grid: Grid,
        bar: int,
        tracks: list[int],
        beat_offset: int,
        chord: str,
        octave: int,
        reverse: bool = False,
        random_order: bool = False,
        duration: int = 1,
        pan: int | None = None,
        volume: int | None = None,
):
    """Spread a chord out over a few beats"""
    chord_notes: list[str] = chords.from_shorthand(chord)
    if random_order:
        shuffle(chord_notes)
    elif reverse:
        chord_notes.reverse()
    for n, i in enumerate(chord_notes):
        grid.add(
            bars=[bar], tracks=tracks, beats=[n+beat_offset], value=i,
            is_chord=IsChord.NO, duration=duration, pan=pan, volume=volume, octave=octave
        )


def test4():
    grid = Grid(granularity=Granularity.EIGHTH)
    grid.add(bars=[0, 1, 2, 3], tracks=[0, ], beats=[WILDCARD], value="hat1", duration=1)
    grid.add(bars=[0, 1, 2, 3], tracks=[0, ], beats=[0, 5], value="kick1", duration=2)
    grid.add(bars=[0, 1, 2, 3], tracks=[0, ], beats=[2, 6], value="snare1", duration=2)
    progression = ("Amin11", "D7", "Fmaj7", "Cmaj7")
    for bar, value in enumerate(progression):
        grid.add(
            bars=[bar, ],
            tracks=[1, ],
            beats=[0, 4, ],
            value=value,
            is_chord=IsChord.YES,
            duration=4,
            velocity=50,
            volume=50,
            pan=-15,
        )
        # Don't take the entire chord, only the root
        grid.add(
            bars=[bar, ],
            tracks=[2, ],
            beats=[2, ],
            value=value,
            is_chord=IsChord.NO,
            duration=1,
            velocity=40,
            octave=4,
            pan=15,
        )
        grid.add(
            bars=[bar], tracks=[3], beats=[0], value=value,
            is_chord=IsChord.NO, duration=0, velocity=0, pan=-20, octave=5
        )
        if value == "Fmaj7":
            chord_spread(grid, bar, [3], 0, "Fmaj7", 5, random_order=True, pan=-20, volume=70)

    grid.copy_to_end(bars=[0, 1, 2, 3], tracks=[0, 1, 2, 3], count=1)
    grid.add(bars=[7], tracks=[0, ], beats=[6, 7], value="hat2", duration=1)
    grid.add(bars=[7], tracks=[0, ], beats=[6], value="kick1", duration=2)
    grid.add(bars=[7], tracks=[0, ], beats=[7], value="snare2", duration=2)
    grid.save('test.mdc', velocity_jitter=13, humanize_jitter=False)
    # Convert the test.mdc file to test.midi file
    converter = Converter(tempo=100)
    converter.convert("test.mdc")
    converter.save("test.midi")


if __name__ == "__main__":
    test4()
