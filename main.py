#!/usr/bin/env python3
import argparse
import os
import subprocess

def parse_time(time_str):
    """
    Convert a time string (hh:mm:ss, mm:ss, or ss) into seconds as a float.
    """
    parts = time_str.split(':')
    try:
        parts = [float(p) for p in parts]
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid time format: {time_str}")
    seconds = 0.0
    for part in parts:
        seconds = seconds * 60 + part
    return seconds

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Remove a portion of a video file using FFmpeg with precise trimming or removal from start/end."
    )
    parser.add_argument(
        "input_file",
        help="Path to the input video file"
    )
    parser.add_argument(
        "--from",
        dest="start",
        help="Start time of the segment to remove (format: hh:mm:ss, mm:ss or ss)"
    )
    parser.add_argument(
        "--to",
        dest="end",
        help="End time of the segment to remove (format: hh:mm:ss, mm:ss, ss or END)"
    )

    # Allow flags and positional arguments to be mixed
    args = parser.parse_intermixed_args()

    # Ensure at least one of --from or --to is provided
    if args.start is None and (args.end is None or args.end.upper() == "END"):
        parser.error("You must specify at least --from or --to.")

    input_file = args.input_file
    base, _ = os.path.splitext(input_file)
    output_file = f"{base}.new.mp4"

    # Determine which arguments are provided
    has_start = args.start is not None
    has_end = args.end is not None and args.end.upper() != "END"

    # Parse times
    start_sec = parse_time(args.start) if has_start else None
    end_sec = parse_time(args.end) if has_end else None

    # Validate time order
    if has_start and has_end and end_sec <= start_sec:
        parser.error("`--to` time must be greater than `--from` time.")

    filter_segments = []

    # Case: only --from provided -> remove from start_sec to end of file
    if has_start and not has_end:
        # Keep only the tail part after start_sec
        filter_segments.append(f"[0:v]trim=start={start_sec},setpts=PTS-STARTPTS[v1];")
        filter_segments.append(f"[0:a]atrim=start={start_sec},asetpts=PTS-STARTPTS[a1];")
        filter_segments.append("[v1][a1]concat=n=1:v=1:a=1[outv][outa]")

    # Case: only --to provided -> remove from start of file to end_sec
    elif has_end and not has_start:
        # Keep only the head part after end_sec
        filter_segments.append(f"[0:v]trim=start={end_sec},setpts=PTS-STARTPTS[v1];")
        filter_segments.append(f"[0:a]atrim=start={end_sec},asetpts=PTS-STARTPTS[a1];")
        filter_segments.append("[v1][a1]concat=n=1:v=1:a=1[outv][outa]")

    # Case: both --from and --to provided -> remove middle segment
    else:
        # Keep head segment from 0 to start_sec
        filter_segments.append(f"[0:v]trim=start=0:end={start_sec},setpts=PTS-STARTPTS[v0];")
        filter_segments.append(f"[0:a]atrim=start=0:end={start_sec},asetpts=PTS-STARTPTS[a0];")
        # Keep tail segment from end_sec to EOF
        filter_segments.append(f"[0:v]trim=start={end_sec},setpts=PTS-STARTPTS[v1];")
        filter_segments.append(f"[0:a]atrim=start={end_sec},asetpts=PTS-STARTPTS[a1];")
        filter_segments.append("[v0][a0][v1][a1]concat=n=2:v=1:a=1[outv][outa]")

    filter_complex = ''.join(filter_segments)

    # Build FFmpeg command
    cmd = [
        "ffmpeg", "-y", "-i", input_file,
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-c:a", "aac",
        output_file
    ]

    print("Running: " + " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"Output written to {output_file}")

if __name__ == "__main__":
    main()
