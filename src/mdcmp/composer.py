from pathlib import Path
from midiutil import MIDIFile
from .converter import Converter
from .constants import FORMAT_VERSION
# from .grid import Grid


class Composer:
    def __init__(
        self,
        tempo: int,
        mdc_format_version: int = FORMAT_VERSION,
        midifile_obj: MIDIFile | None = None,
    ):
        self.midi = (
            midifile_obj
            if midifile_obj
            else MIDIFile(numTracks=128, deinterleave=False)
        )
        self.converter = Converter(
            tempo=tempo, midifile_obj=self.midi, mdc_format_version=mdc_format_version
        )
        self.bank: dict[str, str] = {}

    def load_mdc_bank(self, path_dir: str):
        """
        Create a dictionary for referncing mdc files.

        This will take the last directory and filename to make a reference key.
        Example: data/mdc/misc/test.mdc converts to
            {"misc.mdc": "data/mdc/misc/test.mdc"}
        """
        for path in Path(path_dir).rglob("*.mdc"):
            key = f"{path.parts[-2]}.{path.parts[-1].removesuffix('.mdc')}"
            self.bank[key] = str(path.joinpath())
            print(key, ':', self.bank[key])

    def convert_mdc(self, key: str):
        value: str = self.bank.get(key, '')
        if not value:
            raise KeyError(f"Key not found in self.bank: {key}")
        self.converter.convert(value)

    def save(self, path: str):
        self.converter.save(path)


