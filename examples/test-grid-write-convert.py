from random import shuffle
from mdcmp.grid import Grid, Granularity, IsChord
from mdcmp.constants import ALL as ALL_ITEMS
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
    beat: int = 0
    for n, i in enumerate(chord_notes):
        if n + beat_offset >= grid.number_of_beats:
            print("FIXUP")
            beat = 0
            bar += 1
        grid.add(
            bars=[bar], tracks=tracks, beats=[beat + beat_offset], value=i,
            is_chord=IsChord.NO, duration=duration, pan=pan, volume=volume, octave=octave
        )
        beat += 1


def test4():
    grid = Grid(granularity=Granularity.EIGHTH)
    grid.add(bars=[0, 1, 2, 3], tracks=[0, ], beats=[ALL_ITEMS], value="hat1", duration=1)
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
        # Add rest for copy_to_end below (otherwise it will not work)
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
    grid.copy_to_end(bars=[0, 1, 2, 3, 4, 5, 6, 7], tracks=[0, 1, 2, 3], count=20)
    # grid.save('data/mdc/misc/test.mdc', velocity_jitter=13, humanize_jitter=False)
    grid.save('data/mdc/misc/test.mdc', velocity_jitter=10, humanize_jitter=False)
    # Convert the test.mdc file to test.midi file
    converter = Converter(tempo=100)
    converter.convert("data/mdc/misc/test.mdc")
    converter.save("midi/test.midi")


if __name__ == "__main__":
    test4()
