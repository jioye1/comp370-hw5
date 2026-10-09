#!/usr/bin/env python3
"""Precompute monthly average create-to-closed time (hours) per zipcode.

Reads the trimmed 2024 311 CSV line by line and writes a small CSV with one
row per (zipcode, month), plus rows for zipcode "ALL" covering every zipcode.
Each incident is assigned to the month it was closed. Incidents that are not
closed, or whose closed date is before the created date, are dropped.
"""

import argparse
import csv
from collections import defaultdict
from datetime import datetime

FMT = "%m/%d/%Y %I:%M:%S %p"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--input", required=True, metavar="FILE",
                        help="trimmed 2024 311 CSV file")
    parser.add_argument("-o", "--output", default="monthly_averages.csv",
                        metavar="FILE", help="output CSV (default: %(default)s)")
    args = parser.parse_args()

    sums = defaultdict(float)
    counts = defaultdict(int)
    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        created_i = header.index("Created Date")
        closed_i = header.index("Closed Date")
        zip_i = header.index("Incident Zip")
        for row in reader:
            zipcode, closed = row[zip_i], row[closed_i]
            if not zipcode or not closed:
                continue
            start = datetime.strptime(row[created_i], FMT)
            end = datetime.strptime(row[closed_i], FMT)
            hours = (end - start).total_seconds() / 3600
            if hours < 0:
                continue
            month = end.strftime("%Y-%m")
            for key in ((zipcode, month), ("ALL", month)):
                sums[key] += hours
                counts[key] += 1

    with open(args.output, "w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["zipcode", "month", "avg_hours", "count"])
        for key in sorted(sums):
            writer.writerow([key[0], key[1], round(sums[key] / counts[key], 4),
                             counts[key]])


if __name__ == "__main__":
    main()
