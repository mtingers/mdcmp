import random
import sys
from midiutil import MIDIFile
from .drummap import DRUMS_R
from .util import NOTE_TYPE_MAP, NOTE_TYPE_TO_DURATION
from .util import note_to_offset
from .exceptions import (
    DrumFormatError,
    DrumLineError,
    InvalidNoteError,
    DrumNotFoundError,
)


def _get_drum(startswith: str):
    """Pick a drum by name fuzzily"""
    pick: int = -1
    try:
        pick = DRUMS_R[
            random.choice(
                [
                    i
                    for i in DRUMS_R.keys()
                    if i.startswith(startswith) or i.endswith(startswith)
                ]
            )
        ]
    except IndexError:
        raise DrumNotFoundError(f"Unknown drum {startswith}")
    if pick < 0:
        raise DrumNotFoundError(f"Unknown drum {startswith}")
    return pick


def drums_to_duration(drums_data: str):
    """Calculate a drum format data total duration (add up all of the notes)."""
    _, offset, pattern = drums_data.split("|")
    offset = float(offset)
    patterns = pattern.split(";")
    timer = 0.0 + offset
    for pattern in patterns:
        if not pattern.strip():
            continue
        note_type, _, _ = pattern.split(",")
        try:
            increment = NOTE_TYPE_MAP[note_type]
        except KeyError:
            raise InvalidNoteError(f"Unknown note type: {note_type}")
        timer += increment
    return timer


class Generator:
    """Generate drum file data."""

    def __init__(self, total_duration: float, moods: list[str]):
        """
        total_duration is the length of the output.
        movements_in_order is a mood describer and how long each mood is.
        This will probably change or moved to a different class and is currently unused.
        """
        self.total_duration: float = total_duration
        self.moods: list[str] = moods
        self._gens: list[str] = []

    def _duration_note_to_offset(self, duration: float, note_type: str) -> float:
        """Calculate the offset of a note at a duration."""
        m = NOTE_TYPE_TO_DURATION[note_type]
        duration = float(duration * m)
        return duration

    def gen1(self):
        # kick, snare, hat
        self.gen_track("kick1", self.total_duration, "h", velocity=55)
        self.gen_track("snare1", self.total_duration, "h", velocity=50, time_offset=1)
        self.gen_track("hat1", self.total_duration, "e", velocity=50)
        self.gen_track(
            "hat1",
            self.total_duration,
            "s",
            velocity=50,
            time_offset=self.total_duration,
        )

    def rng1(
        self,
        drum: str,
        allowed_types: list[str],
        nitems: int = 1,
        time_offset: float = 0,
    ):
        """Generate a random drums part using w,h,q,e,s"""
        # output = f'{drum}|{random.choice([0, 0, 0, 0, 1, 1, 2])}|'
        output = f"{drum}|{time_offset}|"
        for _ in range(nitems):
            note_type = random.choice(
                [i for i in list(NOTE_TYPE_MAP.keys()) if i in allowed_types]
            )
            velocity = random.randint(0, 100)
            extra = random.choice("0000est")
            output += f"{note_type},{extra},{velocity};"
        return output

    def rng2(
        self,
        drum: str,
        allowed_types: list[str],
        preferred_types: list[str],
        nitems: int = 1,
        time_offset: int = 0,
    ):
        """Generate a random drums part using w,h,q,e,s"""
        # output = f'{drum}|{random.choice([0, 0, 0, 0, 1, 1, 2])}|'
        output = f"{drum}|{time_offset}|"
        note_type = preferred_types[0]
        for _ in range(nitems):
            while 1:
                note_type = random.choice(
                    [i for i in list(NOTE_TYPE_MAP.keys()) if i in allowed_types]
                )
                if note_type in preferred_types:
                    break
                else:
                    if random.randint(0, 10) < 5:
                        break

            velocity = random.randint(0, 100)
            extra = random.choice("0000est")
            output += f"{note_type},{extra},{velocity};"
        return output

    def test1(self):
        """WIP: figuring out methods of generating drums"""
        # kick1|0|h,0,55;h,0,55;h,0,55;h,0,55;h,0,55;h,0,55;h,0,55;h,0,55;h,0,55;h,0,55;h,0,55;h,0,55;h,0,55;h,0,55;h,0,55;h,0,55;
        # kick1|0|
        kick_pattern1 = "q,0,55;e,0,0;s,0,0;s,0,55;h,0,55;"
        # kick_pattern2 = "q,0,55;e,0,0;s,0,0;s,0,55;h,0,55;q,0,55;e,0,0;s,0,50;s,0,0;h,0,55;"
        kick_pattern2 = (
            "q,0,55;e,0,0;s,0,0;s,0,55;h,0,55;q,0,55;e,0,0;s,0,50;s,0,0;h,0,55;"
        )
        self._gens.append("kick1|0|" + (kick_pattern2 * 10))
        ###################
        snare_pat1 = "h,0,44;h,0,40;h,0,42;e,0,0;e,0,50;q,0,0;"
        snare_pat2 = "h,0,44;h,0,40;h,0,42;s,0,0;s,0,30;e,0,35;q,0,0;"
        snare_pat3 = "h,0,44;h,0,40;h,0,44;h,0,40;h,0,44;h,0,40;h,0,44;h,0,40;"
        snare_pat4 = snare_pat3 + snare_pat1 + snare_pat3 + snare_pat2
        self._gens.append("snare2|1|" + (snare_pat4 * 6))
        # self.gen_track('snare1', self.total_duration, 'h', velocity=50, time_offset=1)
        # self.gen_track('hat1', self.total_duration, 'e', velocity=50)
        hat_pat1 = "e,0,33;e,0,39;e,0,33;e,0,40;e,0,23;e,0,33;e,0,44;e,0,36;"
        hat_pat2 = "e,0,33;e,0,39;e,0,33;e,0,40;e,0,23;e,0,33;e,0,44;e,0,36;e,0,33;e,0,39;e,0,33;e,0,40;e,0,23;e,0,33;s,0,44;s,0,36;s,0,32;s,0,0;"
        self._gens.append("hat1|0|" + (hat_pat2 * 5))
        # self._gens.append(self.rng1('tamb', ['h', 'q', 'e'], nitems=10))
        # self._gens.append(self.rng1('hat2', ['q', 'e', 's'], nitems=30))
        # self._gens.append(self.rng1('snare2', ['q', 'e', 's'], nitems=30))
        self._gens.append(self.rng1("kick1", ["q", "e", "s"], nitems=30))
        print("DURATION:", drums_to_duration("snare|1|h,0,44;h,0,44;"))
        print("DURATION:", drums_to_duration("hat1|0|" + (hat_pat1 * 2)))

    def test2(self):
        """WIP: figuring out methods of generating drums"""
        kick_pattern2 = "w,0,55;w,0,45;"
        self._gens.append("kick1|0|" + (kick_pattern2 * 20))
        self._gens.append(
            self.rng2("kick1", ["w", "q", "e", "s"], ["w", "q"], nitems=30)
        )
        hat_pat2 = "e,0,33;e,0,39;e,0,33;e,0,40;e,0,23;e,0,33;e,0,44;e,0,36;e,0,33;e,0,39;e,0,33;e,0,40;e,0,23;e,0,33;s,0,44;s,0,36;s,0,32;s,0,0;"
        self._gens.append("hat1|0|" + (hat_pat2 * 5))
        snare_pat1 = "h,0,44;h,0,40;h,0,42;e,0,0;e,0,50;q,0,0;"
        snare_pat2 = "h,0,44;h,0,40;h,0,42;s,0,0;s,0,30;e,0,35;q,0,0;"
        snare_pat3 = "h,0,44;h,0,40;h,0,44;h,0,40;h,0,44;h,0,40;h,0,44;h,0,40;"
        snare_pat4 = snare_pat3 + snare_pat1 + snare_pat3 + snare_pat2
        self._gens.append("snare2|1|" + (snare_pat4 * 6))
        # self._gens.append(
        # x = self.rng2('snare1', ['q', 'e', 's'], ['e', 's'], nitems=100)
        self._gens.append(
            self.rng2(
                "ridecym", ["w", "q", "e", "s"], ["w", "q"], nitems=30, time_offset=1
            )
        )

    def gen_track(
        self,
        drum: str,
        duration: float,
        note_type: str,
        time_offset: float = 0.0,
        time_extra: int = 0,
        velocity: int = 50,
    ):
        data = f"{drum}|{time_offset}|"
        duration = note_to_offset(duration, note_type)
        for _ in range(1, int(duration) + 1):
            data += f"{note_type},{time_extra},{velocity};"
        self._gens.append(data)

    def write(self, outfile: str):
        data = "\n".join(self._gens)
        with open(outfile, "w") as fd:
            fd.write(data)


class Controller:
    """Read drum file and generate a MIDI file."""

    def __init__(
        self,
        track: int = 1,
        tempo: int = 120,
        velocity: int = 50,
        total_duration: float = 60,
        midi_obj: MIDIFile | None = None,
    ):
        self.track: int = track
        self.tempo: int = tempo
        self.velocity: int = velocity
        self.total_duration: float = total_duration
        if midi_obj:
            self.midi = midi_obj
        else:
            self.midi = MIDIFile(numTracks=128)
            self.midi.addTempo(0, 0, self.tempo)
        self.generator = Generator(self.total_duration, [])

    def _process_drum_pattern(
        self, patterns: list[str], pitch: int, start_offset: float
    ):
        """Convert a single drum format section to MIDI."""
        timer = 0.0 + start_offset
        duration = 1
        increment = 0
        for pattern in patterns:
            if not pattern.strip():
                continue
            note_type, note_extra, velocity = pattern.split(",")
            try:
                increment = NOTE_TYPE_MAP[note_type]
                timer_extra = NOTE_TYPE_MAP[note_extra]
            except KeyError as err:
                raise InvalidNoteError(
                    f"Unknown note type: {note_type} {pattern} {err}"
                )
            duration = increment
            self.midi.addNote(
                self.track, 0, pitch, timer + timer_extra, duration, int(velocity)
            )
            timer += increment

    def process_drum_file(self, path: str):
        """Convert a drum formatted file to MIDI."""
        with open(path) as drums_fd:
            data = drums_fd.read().strip().split("\n")
        for line_num, i in enumerate(data):
            if not i.strip():
                continue
            if "|" not in i:
                raise DrumLineError(f"Invalid line: {i}")
            try:
                drum, offset, pattern = i.split("|")
            except ValueError:
                raise DrumFormatError(f"Invalid format on line: {line_num}")
            print(drum, offset, pattern)
            drum_note = _get_drum(drum)
            patterns = pattern.split(";")
            self._process_drum_pattern(patterns, drum_note, float(offset))

    def write(self, path: str):
        """Write all tracks stored in self.midi to a MIDI file."""
        with open(path, "wb") as output_file:
            self.midi.writeFile(output_file)


def main():
    drummer = Controller(tempo=60, total_duration=120)
    gen = drummer.generator
    gen.test2()
    gen.write(sys.argv[1])
    drummer.process_drum_file(sys.argv[1])
    drummer.write(sys.argv[2])
