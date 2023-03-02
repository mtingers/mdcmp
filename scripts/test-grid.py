from mdcmp.grid import Grid, Granularity


def main():
    grid = Grid(granularity=Granularity.EIGHTH)
    grid.add(beats=[1, 5], bars=[1, 2], value='kick1', tracks=[1], duration=2, volume=40)
    grid.add(beats=[3, 7], bars=[1, 2], value='snare1', tracks=[1], duration=2)
    grid.add(beats=[-1], bars=[1, 2], value='hat1', tracks=[1], duration=1)
    grid.add(beats=[1], bars=[1], value='Cm7', tracks=[2], duration=2)
    grid.add(beats=[1], bars=[2], value='Cm7', tracks=[2], duration=2)
    grid.add(beats=[3], bars=[1, 2, 3], value='Eb', tracks=[2], duration=2)
    grid.copy_to_end(bars=[1], tracks=[1, 2], count=2)
    grid.dump_grid()


if __name__ == '__main__':
    main()
