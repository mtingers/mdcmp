from mdcmp.grid import Grid, Granularity, WILDCARD, IsChord


def test1():
    grid = Grid(granularity=Granularity.EIGHTH)
    grid.add(bars=[0,], tracks=[0,], beats=[0, 4], value='kick1', duration=[2, 2], volume=40)
    grid.add(bars=[0,], tracks=[0,], beats=[2, 6], value='snare1', duration=2, volume=40)
    grid.add(bars=[0,], tracks=[0,], beats=[WILDCARD], value='hat1')
    # Instrument tracks
    grid.add(bars=[0, 1, 2], tracks=[1,], beats=[WILDCARD], value='C#', octave=2)
    grid.add(bars=[0, 1, 2], tracks=[2,], beats=[WILDCARD], value='C#', octave=4)
    grid.add(bars=[0, 1, 2], tracks=[2, 1], beats=[0, 3, 7], value='A#', is_chord=IsChord.YES)
    grid.add(bars=[9,], tracks=[0,], beats=[0, 4], value='kick1', duration=[2, 2], volume=40)
    grid.dump_grid()
    print('-'*80)
    print('After copy:')
    grid.copy_to_end(bars=[0], tracks=[0, 1], count=2)
    grid.dump_grid()
    print('-'*80)
    print('After transform:')
    grid.transform(
        # bars=[0,], tracks=[0, 1], beats=[WILDCARD],
        bars=[WILDCARD,], tracks=[WILDCARD], beats=[WILDCARD],
        duration=10, volume=127, is_chord=IsChord.NO,
    )
    grid.dump_grid()
    grid.to_data()


def test2():
    grid = Grid(granularity=Granularity.EIGHTH)
    grid.add(bars=[0,], tracks=[0,], beats=[WILDCARD], value='hat1')
    # Instrument tracks
    grid.add(bars=[2,], tracks=[0,], beats=[0, 4], value='kick1', duration=[2, 2], volume=40)
    grid.add(bars=[6,], tracks=[1,], beats=[0, 4], value='kick1', duration=[2, 2], volume=40)
    grid.fill_gaps()
    grid.dump_grid()
    grid.to_data()
    # grid.dump_grid()


def test3():
    grid = Grid(granularity=Granularity.EIGHTH)
    grid.add(bars=[1,], tracks=[0,], beats=[WILDCARD], value='hat1', duration=1)
    grid.add(
        bars=[1, ], tracks=[0, ], beats=[0, 1, 2, 3, 4, 5, 6, ],
        value='snare1', duration=[1, 1, 1, 2, 2, 2, 3],
        volume=17,

    )
    grid.add(bars=[1,], tracks=[1,], beats=[0, 1, 2], value='Cmin7', is_chord=True, duration=1)
    grid.add(bars=[1,], tracks=[2,], beats=[0, 1, 2], value='Cmin7', is_chord=False, duration=1)
    # Instrument tracks
    grid.dump_grid()
    grid.to_data()


if __name__ == '__main__':
    test3()
