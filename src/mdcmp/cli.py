"""
Generate MIDI songs from the CLI.
"""
import argparse
import random
from .composer import Controller as ComposerController
from .composer import Generator as ComposerGenerator
from .drummer import Controller as DrumController
from .drummer import Generator as DrumGenerator

# --duration N
# --bpm N
# --out path.midi
#
#
# --drums-out path
# --composition-out path
# --compositions N
# --drums t|f
# --composition-in path1,path2,...
# --drums-in path1,path2,...
# --drums-loop path1,path2,...
# --composition-loop path1,path2,...


def run(args):
    composer: ComposerController = ComposerController(
        tempo=args.bpm, total_duration=args.duration
    )
    generator: ComposerGenerator = composer.generator
    drum_controller: DrumController = composer.drum_controller
    drum_generator: DrumGenerator = drum_controller.generator


def cli():
    parser = argparse.ArgumentParser(
        prog="mdcmp", description="Generate MIDI songs from the CLI", epilog=""
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=int,
        help="The time in seconds of the generated song",
        required=True,
    )
    parser.add_argument(
        "-b", "--bpm", type=int, help="Tempo, beats per minute", required=True
    )
    parser.add_argument(
        "-o", "--out", type=str, help="Output path of MIDI file", required=True
    )
    args = parser.parse_args()
    run(args)
