"""
Translate MDC files to MIDI files.
"""
from typing import Any
from midiutil import MIDIFile
from mingus.core.notes import RangeError

from .exceptions import PitchNotFoundError
from .constants import NOTE_TIME_MAP, KNOWN_MDC_FORMAT_VERSIONS, EVENT_MAP
from .exceptions import (
    MdcInvalidNoteError,
    MdcLineError,
    MdcFormatError,
    MdcUnknownVersionError,
    MdcInvalidGranularityError,
    MdcAlignmentError,
)


class Converter:
    def __init__(
        self,
        tempo: int = 120,
        track: int = 0,
        midifile_obj: MIDIFile | None = None,
        mdc_format_version: int = 1,
    ):
        """
        Args:
            tempo (int): The tempo in BPM (beats per minute).
            track (int): The track number to start at. Useful if midifile_obj is passed around and
                         mutated elsewhere. Otherwise, ignore this value.
            midifile_obj (midiutil.MIDIFile): A class that encapsulates a MIDI file object.
            mdc_format_version (int): The MDC format version of in the input file.
        """
        self.track: int = track
        self.mdc_format_version: int = mdc_format_version
        self.midi = (
            midifile_obj
            if midifile_obj
            else MIDIFile(numTracks=128, deinterleave=False)
        )
        self.midi.addTempo(0, 0, tempo)

    def _split_data(self, data: str, map_type: Any) -> Any:
        if "!" in data:
            return list(map(map_type, data.split("!")))
        return map_type(data)

    def _validate(
        self,
        pitches: list[int] | int,
        note_types: list[str] | str,
        note_paddings: list[str] | str,
        velocities: list[int] | int,
    ):
        # Validate note types
        if isinstance(note_types, list):
            for note_type in note_types:
                if note_type not in NOTE_TIME_MAP.keys():
                    raise MdcInvalidNoteError(f"Unknown note type: {note_type}")
        # Validate note_paddings
        if isinstance(note_paddings, list):
            for note_padding in note_paddings:
                if note_padding not in NOTE_TIME_MAP.keys():
                    raise MdcInvalidNoteError(f"Unknown note extra: {note_padding}")
        # Validate pitches
        if isinstance(pitches, list):
            for pitch in pitches:
                if pitch < 0 or pitch > 127:
                    raise PitchNotFoundError(f"Invalid pitch: {pitch}")
        else:
            if pitches < 0 or pitches > 127:
                raise PitchNotFoundError(f"Invalid pitch: {pitches}")

        # Validate list sizes match len(pitches)
        for i in (note_types, note_paddings, velocities):
            if isinstance(pitches, list):
                if isinstance(i, list) and len(i) != len(pitches):
                    raise MdcAlignmentError(
                        "Invalid data alignment to pitches."
                    )  # TODO
            else:
                if isinstance(i, list):
                    raise MdcAlignmentError(
                        "Invalid data alignment to single pitch."
                    )  # TODO

    def _convert_patterns_v1(
        self, patterns: list[str], granularity: str, track_type: str, start_offset: float
    ):
        """
        Convert a single line of the composer format data to midi.

        Args:
            patterns (list[str]): The data section of the MDC format in list format.
            granularity (str): The grid granularity to quantize to.
            track_type (str): Describes the type of track. Either "drum" or "instrument".
            start_offset (float): The time offset in which the track starts.
        """
        timer: float = 0.0 + start_offset
        increment: float = NOTE_TIME_MAP.get(granularity, 0.0)
        channel: int = 9 if track_type == "drum" else 0
        if increment == 0.0:
            raise MdcInvalidGranularityError(f"Unknown granularity: {granularity}")
        for pattern in patterns:
            # Forgive extra spacing
            if not pattern.strip():
                continue

            try:
                (
                    pitches,
                    note_types,
                    note_paddings,
                    velocities,
                    volume,
                    pitchwheel,
                    modwheel,
                    expression,
                    sustain,
                    pan
                ) = pattern.split(",")
            except ValueError as err:
                raise Exception(f"Failed to parse pattern (len={len(pattern.split(','))}): {pattern}    err={err}")
            try:
                pitches = self._split_data(pitches, int)
                note_types = self._split_data(note_types, str)
                note_paddings = self._split_data(note_paddings, str)
                velocities = self._split_data(velocities, int)
            except Exception as err:
                raise Exception(f"Unknown error parsing mdc data: {err}")

            self._validate(pitches, note_types, note_paddings, velocities)
            event_items = {
                'volume': volume,
                'pitchwheel': pitchwheel,
                'modwheel': modwheel,
                'expression': expression,
                'sustain': sustain,
                'pan': pan,
            }
            # validate track automations
            for item in event_items.values():
                if item == "n":
                    continue
                item = int(item)
                if item < 0 or item > 127:
                    raise RangeError(f"Value is out of range (0-127): {item}")

            # Handle events first
            for event_name, value in event_items.items():
                event_int: int | None = EVENT_MAP.get(event_name, 0)
                if event_int is not None and event_int < 1:
                    continue  # Raise exception?
                if value in ("n", ):
                    continue
                value = int(value)
                if event_name == "pitchwheel":
                    self.midi.addPitchWheelEvent(self.track, channel, timer, value)
                else:
                    self.midi.addControllerEvent(self.track, channel, timer, event_int, value)

            # Layer the pitches and settings onto a single MIDI track
            if isinstance(pitches, list):
                for n, pitch in enumerate(pitches):
                    if isinstance(note_types, list):
                        note_type = NOTE_TIME_MAP.get(note_types[n], 0.0)
                    else:
                        note_type = NOTE_TIME_MAP.get(note_types, 0.0)
                    if isinstance(note_paddings, list):
                        note_padding = NOTE_TIME_MAP.get(note_paddings[n], 0.0)
                    else:
                        note_padding = NOTE_TIME_MAP.get(note_paddings, 0.0)
                    if isinstance(velocities, list):
                        velocity = velocities[n]
                    else:
                        velocity = velocities
                    """
                    print((
                        f'self.midi.addNote({self.track}, {channel}, {pitch},'
                        f'{timer + note_padding}, {note_type}, {velocity})'
                    ))
                    """
                    self.midi.addNote(
                        self.track, channel, pitch, timer + note_padding, note_type, velocity
                    )

            else:
                # All items are a single value and not a list
                note_type = NOTE_TIME_MAP.get(note_types, 0.0)
                note_paddings = NOTE_TIME_MAP.get(note_paddings, 0.0)
                """
                print((
                    f'self.midi.addNote({self.track}, {channel}, {pitches},'
                    f'{timer + note_paddings}, {note_type}, {velocities})'
                ))
                """
                self.midi.addNote(
                    self.track, channel, pitches, timer + note_paddings, note_type, velocities
                )
            # Increment the timer according to the grid granularity
            timer += increment

    def _convert_v1(self, data: list[str]):
        """Version 1 format"""
        """
        """

        for line_num, i in enumerate(data):
            # Forgive blank lines
            if not i.strip():
                continue
            if "|" not in i:
                raise MdcLineError(f"Invalid line {line_num}: {i}")
            try:
                _, track_type, granularity, offset, mdata = i.split("|")
            except ValueError:
                raise MdcFormatError(f"Invalid format on line: {line_num}")
            patterns = mdata.strip().replace("; ", ";").split(";")
            self._convert_patterns_v1(patterns, granularity, track_type, float(offset))
            self.track += 1

    def convert(self, path_to_mdc_file: str):
        """
        Convert a composer format file to midi.

        Args:
            path_to_mdc_file (str): The input file in MDC format.


        """
        """
        MDC format reference (version 1):
            version(int)
            reserved|track-type|granularity|start-offset| track-data...
        """
        with open(path_to_mdc_file) as mdc_fd:
            data = mdc_fd.read().strip().split("\n")
        try:
            mdc_version: int = int(data[0])
            if mdc_version not in KNOWN_MDC_FORMAT_VERSIONS:
                raise MdcUnknownVersionError(
                    f"Unknown mdc format version: {mdc_version}"
                )
        except ValueError:
            raise MdcFormatError("Invalid header. Is this an mdc file?")
        if mdc_version == 1:
            self._convert_v1(data[1:])
        else:
            raise MdcUnknownVersionError(
                f"Unknown mdc format version: {mdc_version}"
            )

    def save(self, path: str):
        """
        Write all tracks stored in self.midi to a MIDI file.

        Args:
            path (str): The output file to write the MIDI data to.
        """
        with open(path, "wb") as output_file:
            self.midi.writeFile(output_file)
