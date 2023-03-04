"""
Translate MDC files to MIDI files.
"""
from typing import Any
from midiutil import MIDIFile

from build.lib.mdcmp.exceptions import PitchNotFoundError
from .constants import NOTE_TIME_MAP, KNOWN_MDC_FORMAT_VERSIONS
from .exceptions import (
    MdcInvalidNoteError,
    MdcLineError,
    MdcFormatError,
    MdcUnknownVersionrror,
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
            track (int): The track number to start at.
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
        note_extras: list[str] | str,
        volumes: list[int] | int,
    ):
        # Validate note types
        if isinstance(note_types, list):
            for note_type in note_types:
                if note_type not in NOTE_TIME_MAP.keys():
                    raise MdcInvalidNoteError(f"Unknown note type: {note_type}")
        # Validate note_extras
        if isinstance(note_extras, list):
            for note_extra in note_extras:
                if note_extra not in NOTE_TIME_MAP.keys():
                    raise MdcInvalidNoteError(f"Unknown note extra: {note_extra}")
        # Validate pitches
        if isinstance(pitches, list):
            for pitch in pitches:
                if pitch < 0 or pitch > 127:
                    raise PitchNotFoundError(f"Invalid pitch: {pitch}")
        else:
            if pitches < 0 or pitches > 127:
                raise PitchNotFoundError(f"Invalid pitch: {pitches}")

        # Validate list sizes match len(pitches)
        for i in (note_types, note_extras, volumes):
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

    def _convert_patterns(
        self, patterns: list[str], granularity: str, start_offset: float
    ):
        """
        Convert a single line of the composer format data to midi.

        Args:
            patterns (list[str]): The data section of the MDC format in list format.
            track_type (str): Describes the type of track. Either "drum" or "instrument".
            start_offset (float): The time offset in which the track starts.
        """
        timer: float = 0.0 + start_offset
        increment: float = NOTE_TIME_MAP.get(granularity, 0.0)
        if increment == 0.0:
            raise MdcInvalidGranularityError(f"Unknown granularity: {granularity}")
        for pattern in patterns:
            # Forgive extra spacing
            if not pattern.strip():
                continue
            pitches, note_types, note_extras, volumes = pattern.split(",")
            try:
                pitches = self._split_data(pitches, int)
                note_types = self._split_data(note_types, str)
                note_extras = self._split_data(note_extras, str)
                volumes = self._split_data(volumes, int)
            except Exception as err:
                raise Exception(f"Unknown error parsing mdc data: {err}")

            self._validate(pitches, note_types, note_extras, volumes)

            # Layer the pitches and settings onto a single MIDI track
            if isinstance(pitches, list):
                for n, pitch in enumerate(pitches):
                    if isinstance(note_types, list):
                        note_type = NOTE_TIME_MAP.get(note_types[n], 0.0)
                    else:
                        note_type = NOTE_TIME_MAP.get(note_types, 0.0)
                    if isinstance(note_extras, list):
                        note_extra = NOTE_TIME_MAP.get(note_extras[n], 0.0)
                    else:
                        note_extra = NOTE_TIME_MAP.get(note_extras, 0.0)
                    if isinstance(volumes, list):
                        volume = volumes[n]
                    else:
                        volume = volumes
                    self.midi.addNote(
                        self.track, 0, pitch, timer + note_extra, note_type, volume
                    )

            else:
                # All items are a single value and not a list
                note_type = NOTE_TIME_MAP.get(note_types, 0.0)
                note_extras = NOTE_TIME_MAP.get(note_extras, 0.0)
                self.midi.addNote(
                    self.track, 0, pitches, timer + note_extras, note_type, volumes
                )
            # Increment the timer according to the grid granularity
            timer += increment

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
                raise MdcUnknownVersionrror(
                    f"Unknown mdc format version: {mdc_version}"
                )
        except ValueError:
            raise MdcFormatError("Invalid header. Is this an mdc file?")
        for line_num, i in enumerate(data):
            # Forgive blank lines
            if not i.strip():
                continue
            if "|" not in i:
                raise MdcLineError(f"Invalid line {line_num}: {i}")
            try:
                _, _, granularity, offset, data = i.split("|")
            except ValueError:
                raise MdcFormatError(f"Invalid format on line: {line_num}")
            patterns = data.strip().replace("; ", "").split(";")
            self._convert_patterns(patterns, granularity, float(offset))
            self.track += 1

    def save(self, path: str):
        """
        Write all tracks stored in self.midi to a MIDI file.

        Args:
            path (str): The output file to write the MIDI data to.
        """
        with open(path, "wb") as output_file:
            self.midi.writeFile(output_file)
