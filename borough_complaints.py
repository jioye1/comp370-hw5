#!/usr/bin/env python3
"""Count NYC 311 complaint types per borough for a range of creation dates."""

import argparse
import csv
import sys
from collections import Counter
from datetime import datetime


def parse_date(text):
    """Parse a YYYY-MM-DD command line date into an ISO string."""
    try:
        return datetime.strptime(text, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid date '{text}' (expected YYYY-MM-DD)")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Output the number of each complaint type per borough "
                    "for incidents created in a date range (inclusive). "
                    "Results are CSV rows: complaint type, borough, count.",
        epilog="example: %(prog)s -i 311_2024.csv -s 2024-01-01 "
               "-e 2024-02-29 -o counts.csv")
    parser.add_argument("-i", "--input", required=True, metavar="FILE",
                        help="input 311 CSV file")
    parser.add_argument("-s", "--start", required=True, type=parse_date,
                        metavar="YYYY-MM-DD",
                        help="start of the creation date range (inclusive)")
    parser.add_argument("-e", "--end", required=True, type=parse_date,
                        metavar="YYYY-MM-DD",
                        help="end of the creation date range (inclusive)")
    parser.add_argument("-o", "--output", metavar="FILE",
                        help="output file (default: print to stdout)")
    return parser


def count_complaints(path, start, end):
    """Return a Counter of (complaint type, borough) for rows in [start, end]."""
    counts = Counter()
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        created_i = header.index("Created Date")
        type_i = header.index("Complaint Type")
        borough_i = header.index("Borough")
        for row in reader:
            # Created Date looks like "MM/DD/YYYY hh:mm:ss AM"
            d = row[created_i]
            iso = f"{d[6:10]}-{d[0:2]}-{d[3:5]}"
            if start <= iso <= end:
                counts[(row[type_i], row[borough_i])] += 1
    return counts


def main():
    args = build_parser().parse_args()
    if args.start > args.end:
        sys.exit("error: start date is after end date")

    counts = count_complaints(args.input, args.start, args.end)

    out = open(args.output, "w", newline="") if args.output else sys.stdout
    try:
        writer = csv.writer(out)
        writer.writerow(["complaint type", "borough", "count"])
        for (ctype, borough), n in sorted(counts.items()):
            writer.writerow([ctype, borough, n])
    finally:
        if args.output:
            out.close()


if __name__ == "__main__":
    main()
