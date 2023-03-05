from mdcmp.grid import Grid, Granularity, WILDCARD, IsChord
from mdcmp.converter import Converter


def test1():
    grid = Grid(granularity=Granularity.EIGHTH)
    grid.add(bars=[0, ], tracks=[0, ], beats=[0, 4], value="kick1", duration=[2, 2], velocity=40,)
    grid.add(bars=[0, ], tracks=[0, ], beats=[2, 6], value="snare1", duration=2, velocity=40,)
    grid.add(bars=[0, ], tracks=[0, ], beats=[WILDCARD], value="hat1",)
    # Instrument tracks
    grid.add(bars=[0, 1, 2], tracks=[1, ], beats=[WILDCARD], value="C#", octave=2,)
    grid.add(bars=[0, 1, 2], tracks=[2, ], beats=[WILDCARD], value="C#", octave=4,)
    grid.add(bars=[0, 1, 2], tracks=[2, 1], beats=[0, 3, 7], value="A#", is_chord=IsChord.YES)
    grid.add(bars=[9, ], tracks=[0, ], beats=[0, 4], value="kick1", duration=[2, 2], velocity=40,)
    grid.dump_grid()
    print("-" * 80)
    print("After copy:")
    grid.copy_to_end(bars=[0], tracks=[0, 1], count=2)
    grid.dump_grid()
    print("-" * 80)
    print("After transform:")
    grid.transform(
        # bars=[0,], tracks=[0, 1], beats=[WILDCARD],
        bars=[WILDCARD],
        tracks=[WILDCARD],
        beats=[WILDCARD],
        duration=10,
        velocity=127,
        is_chord=IsChord.NO,
    )
    grid.dump_grid()
    grid.to_data()


def test2():
    grid = Grid(granularity=Granularity.EIGHTH)
    grid.add(bars=[0, ], tracks=[0, ], beats=[WILDCARD], value="hat1",)
    # Instrument tracks
    grid.add(bars=[2, ], tracks=[0, ], beats=[0, 4], value="kick1", duration=[2, 2], velocity=40,)
    grid.add(bars=[6, ], tracks=[1, ], beats=[0, 4], value="kick1", duration=[2, 2], velocity=40,)
    grid.fill_gaps()
    grid.dump_grid()
    grid.to_data()
    # grid.dump_grid()


def test3():
    grid = Grid(granularity=Granularity.EIGHTH)
    grid.add(bars=[1, ], tracks=[0, ], beats=[WILDCARD], value="hat1", duration=1,)
    grid.add(
        bars=[1, ],
        tracks=[0, ],
        beats=[0, 1, 2, 3, 4, 5, 6, ],
        value="snare1",
        duration=[1, 1, 1, 2, 2, 2, 3],
        velocity=33,
        volume=99,
    )
    grid.add(
        bars=[1, ],
        tracks=[1, ],
        beats=[0, 1, 2],
        value="Cmin7",
        is_chord=IsChord.YES,
        duration=1,
        velocity=50,
        volume=100,
    )
    grid.add(
        bars=[1, ],
        tracks=[2, ],
        beats=[0, 1, 2],
        value="Cmin7",
        is_chord=IsChord.NO,
        duration=1,
        velocity=65,
        volume=75,
    )
    # Instrument tracks
    grid.dump_grid()
    #grid.to_data(velocity_jitter=0, humanize_jitter=False)
    grid.save('test.mdc', velocity_jitter=0, humanize_jitter=False)
    # Convert the test.mdc file to test.midi file
    converter = Converter(tempo=120)
    converter.convert("test.mdc")
    converter.save("test.midi")


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
    grid.copy_to_end(bars=[0, 1, 2, 3], tracks=[0, 1, 2], count=1)
    grid.add(bars=[7], tracks=[0, ], beats=[6, 7], value="hat2", duration=1)
    grid.add(bars=[7], tracks=[0, ], beats=[6], value="kick1", duration=2)
    grid.add(bars=[7], tracks=[0, ], beats=[7], value="snare2", duration=2)
    #grid.to_data(velocity_jitter=0, humanize_jitter=False)
    grid.save('test.mdc', velocity_jitter=10, humanize_jitter=False)
    # Convert the test.mdc file to test.midi file
    converter = Converter(tempo=100)
    converter.convert("test.mdc")
    converter.save("test.midi")


if __name__ == "__main__":
    test4()
