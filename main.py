#!/usr/bin/env python3
import argparse
import os
import subprocess

def parse_time(time_str):
    """
    Parse a time string (hh:mm:ss, mm:ss, or ss) into seconds (float).
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
    parser = argparse.ArgumentParser(
        description="Remove a segment from a video file using FFmpeg with precise trimming or removal from start/end."
    )
    parser.add_argument(
        "input_file",
        help="Path to the input video file"
    )
    parser.add_argument(
        "--from",
        dest="start",
        help="Start time of segment to remove (format hh:mm:ss, mm:ss or ss)"
    )
    parser.add_argument(
        "--to",
        dest="end",
        help="End time of segment to remove (format hh:mm:ss, mm:ss, ss or END)"
    )
    args = parser.parse_args()

    if args.start is None and (args.end is None or args.end.upper() == "END"):
        parser.error("You must specify at least --from or a --to time.")

    input_file = args.input_file
    base, _ = os.path.splitext(input_file)
    output_file = f"{base}.new.mp4"

    have_start = args.start is not None
    have_end = args.end is not None and args.end.upper() != "END"

    # Determine times
    start_sec = parse_time(args.start) if have_start else 0.0
    end_sec = parse_time(args.end) if have_end else None

    # Validate times
    if have_start and have_end and end_sec <= start_sec:
        parser.error("`--to` time must be greater than `--from` time.")

    # Build filter_complex
    filter_parts = []

    # Case: remove from start until end => keep tail only
    if not have_start and have_end:
        f1 = f"[0:v]trim=start={end_sec},setpts=PTS-STARTPTS[v1];"
        a1 = f"[0:a]atrim=start={end_sec},asetpts=PTS-STARTPTS[a1];"
        filter_parts.extend([f1, a1, "[v1][a1]concat=n=1:v=1:a=1[outv][outa]"])

    # Case: remove from start to EOF => keep head only
    elif have_start and not have_end:
        f0 = f"[0:v]trim=start=0:end={start_sec},setpts=PTS-STARTPTS[v0];"
        a0 = f"[0:a]atrim=start=0:end={start_sec},asetpts=PTS-STARTPTS[a0];"
        filter_parts.extend([f0, a0, "[v0][a0]concat=n=1:v=1:a=1[outv][outa]"])

    # Case: remove a middle segment => keep head and tail
    else:
        f0 = f"[0:v]trim=start=0:end={start_sec},setpts=PTS-STARTPTS[v0];"
        a0 = f"[0:a]atrim=start=0:end={start_sec},asetpts=PTS-STARTPTS[a0];"
        f1 = f"[0:v]trim=start={end_sec},setpts=PTS-STARTPTS[v1];"
        a1 = f"[0:a]atrim=start={end_sec},asetpts=PTS-STARTPTS[a1];"
        filter_parts.extend([f0, a0, f1, a1, "[v0][a0][v1][a1]concat=n=2:v=1:a=1[outv][outa]"])

    filter_complex = ''.join(filter_parts)

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
