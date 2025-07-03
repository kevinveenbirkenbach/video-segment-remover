#!/usr/bin/env python3
import argparse
import os
import subprocess
import tempfile

def run_ffmpeg(cmd):
    """
    Helper to run an ffmpeg command and print it.
    """
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def main():
    parser = argparse.ArgumentParser(
        description="Remove a segment from a video file using ffmpeg."
    )
    parser.add_argument(
        "input_file",
        help="Input video file"
    )
    parser.add_argument(
        "--from",
        dest="start",
        required=True,
        help="Start time of the segment to remove (format hh:mm:ss)"
    )
    parser.add_argument(
        "--to",
        dest="end",
        required=True,
        help="End time of the segment to remove (format hh:mm:ss or END)"
    )
    args = parser.parse_args()

    input_file = args.input_file
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}.new.mp4"

    with tempfile.TemporaryDirectory() as tmpdir:
        part1 = os.path.join(tmpdir, "part1.mp4")
        part2 = os.path.join(tmpdir, "part2.mp4")
        files_txt = os.path.join(tmpdir, "files.txt")

        # Extract the segment before the removal start
        cmd1 = [
            "ffmpeg", "-y", "-i", input_file,
            "-ss", "00:00:00", "-to", args.start,
            "-c", "copy", part1
        ]
        run_ffmpeg(cmd1)

        # If removing until end, just rename part1 to output
        if args.end.upper() == "END":
            os.replace(part1, output_file)
            print(f"Output written to {output_file}")
            return

        # Extract the segment after the removal end
        cmd2 = [
            "ffmpeg", "-y", "-ss", args.end, "-i", input_file,
            "-c", "copy", part2
        ]
        run_ffmpeg(cmd2)

        # Create the concat list
        with open(files_txt, "w") as f:
            f.write(f"file '{part1}'\nfile '{part2}'\n")

        # Concatenate parts
        cmd_concat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", files_txt, "-c", "copy", output_file
        ]
        run_ffmpeg(cmd_concat)

    print(f"Output written to {output_file}")

if __name__ == "__main__":
    main()
