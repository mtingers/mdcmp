from mdcmp.grid import Grid, Granularity, WILDCARD, IsChord


def main2():
    grid = Grid(granularity=Granularity.EIGHTH)
    grid.add(bars=[0,], tracks=[0,], beats=[0, 4], value='kick1', duration=2, volume=40)
    grid.add(bars=[0,], tracks=[0,], beats=[2, 6], value='snare1', duration=2, volume=40)
    grid.add(bars=[0,], tracks=[0,], beats=[WILDCARD], value='hat1')
    # Instrument tracks
    grid.add(bars=[0, 1, 2], tracks=[1,], beats=[WILDCARD], value='C#')
    grid.add(bars=[0, 1, 2], tracks=[2,], beats=[WILDCARD], value='C#')
    grid.add(bars=[0, 1, 2], tracks=[2, 1], beats=[0,3,7], value='A#', is_chord=IsChord.YES)
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
        duration=33, volume=127, is_chord=IsChord.NO,
    )
    """
    grid.transform(
        bars=[1,], tracks=[0,], beats=[WILDCARD],
        duration=33, volume=127, is_chord=IsChord.NO,
    )
    """
    grid.dump_grid()


if __name__ == '__main__':
    main2()
