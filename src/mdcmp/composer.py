import random
import sys
from midiutil import MIDIFile
from .util import NOTE_TYPE_MAP
from .util import note_to_offset
from .exceptions import ComposerLineError, ComposerFormatError, InvalidNoteError
from .drummer import Controller as DrumController


def composition_to_duration(composition_data: str):
    """Calculate a composition's total duration (add up all of the notes)."""
    offset, pattern = composition_data.split("|")
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
    """Generate composer file data."""

    def __init__(self, total_duration: float, moods: list[str]):
        """
        total_duration is the length of the output.
        movements_in_order is a mood describer and how long each mood is.
        This will probably change or moved to a different class and is currently unused.
        """
        self.total_duration: float = total_duration
        self.moods: list[str] = moods
        self._gens: list[str] = []

    def gen1(self):
        pass

    def rng1(self, allowed_types: list[str], nitems: int = 1, time_offset: int = 0):
        """Generate a random composition part using notes w,h,q,e,s,t"""
        output = f"{time_offset}|"
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
        allowed_types: list[str],
        preferred_types: list[str],
        nitems: int = 1,
        time_offset: int = 0,
    ):
        """Generate a random composition part using w,h,q,e,s,t"""
        output = f"{time_offset}|"
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

    def gen_track(
        self,
        duration: float,
        note_type: str,
        time_offset: float = 0.0,
        time_extra: float = 0,
        velocity: int = 50,
    ):
        """
        A mostly useless general purpose generator that uses a constant note type
        (e.g. quarter note).
        This can be useful for testing or generating a kick or hi-hat that repeats.
        """
        data = f"{time_offset}|"
        duration = note_to_offset(duration, note_type)
        for _ in range(1, int(duration) + 1):
            data += f"{note_type},{time_extra},{velocity};"
        self._gens.append(data)

    def write(self, outfile: str):
        data = "\n".join(self._gens)
        with open(outfile, "w") as fd:
            fd.write(data)


class Controller:
    """Read composer and drum file and combine them to generate a MIDI file."""

    def __init__(
        self,
        track: int = 1,
        tempo: int = 120,
        velocity: int = 50,
        total_duration: float = 60.0,
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
        self.drum_controller: DrumController = DrumController(
            track=0,
            tempo=self.tempo,
            total_duration=self.total_duration,
            midi_obj=self.midi,
        )

    def _process_composition_pattern(self, patterns: list[str], start_offset: float):
        """Convert a single line of the composer format data to midi."""
        # format: start-time-offset|pitch,note,note-additional-time,volume|velocity;...
        # 0|33,q,0,100;
        timer: float = 0.0 + start_offset
        duration: float = 1.0
        increment: float = 0
        for pattern in patterns:
            if not pattern.strip():
                continue
            pitch, note_type, note_extra, velocity = pattern.split(",")
            pitch = int(pitch)
            assert pitch >= 0 and pitch <= 127
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

    def process_composition_file(self, path: str):
        """Convert a composer format file to midi."""
        with open(path) as composition_fd:
            data = composition_fd.read().strip().split("\n")
        for line_num, i in enumerate(data):
            if not i.strip():
                continue
            if "|" not in i:
                raise ComposerLineError(f"Invalid line: {i}")
            try:
                offset, pattern = i.split("|")
            except ValueError:
                raise ComposerFormatError(f"Invalid format on line: {line_num}")
            print(offset, pattern)
            patterns = pattern.split(";")
            self._process_composition_pattern(patterns, float(offset))
            self.track += 1

    def process_composition_and_drum_file(self, composition_path: str, drums_path: str):
        """Process a composition and drums file to output together on write() call."""
        self.process_composition_file(composition_path)
        self.drum_controller.process_drum_file(drums_path)

    def write(self, path: str):
        """Write all tracks stored in self.midi to a MIDI file."""
        with open(path, "wb") as output_file:
            self.midi.writeFile(output_file)


def main():
    controller = Controller(tempo=60, total_duration=120)
    # gen = controller.generator
    # gen.lofi2()
    # gen.write(sys.argv[1])
    controller.process_composition_file(sys.argv[1])
    controller.write(sys.argv[2])


def combiner():
    # TODO: add argparser
    controller = Controller(tempo=60, total_duration=120)
    controller.process_composition_and_drum_file(sys.argv[1], sys.argv[2])
    controller.write(sys.argv[3])
