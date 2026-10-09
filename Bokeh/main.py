"""Bokeh dashboard: monthly average 311 create-to-closed time by zipcode.

Run preprocess.py first to create monthly_averages.csv, then:
    bokeh serve Bokeh      (from the directory containing this folder)
"""

import csv
from collections import defaultdict
from datetime import datetime
from os.path import dirname, join

from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Legend, LegendItem, Select
from bokeh.plotting import curdoc, figure

DATA_FILE = join(dirname(__file__), "monthly_averages.csv")
YEAR = "2024"  # months (by closed date) shown on the plot

# series[zipcode] = {month: avg_hours}; "ALL" holds the overall average
series = defaultdict(dict)
totals = defaultdict(int)
with open(DATA_FILE, newline="") as f:
    for row in csv.DictReader(f):
        if row["month"].startswith(YEAR):
            series[row["zipcode"]][row["month"]] = float(row["avg_hours"])
            totals[row["zipcode"]] += int(row["count"])

months = [f"{YEAR}-{m:02d}" for m in range(1, 13)]
month_dates = [datetime.strptime(m, "%Y-%m") for m in months]
zipcodes = sorted(z for z in series if z != "ALL")
by_volume = sorted(zipcodes, key=lambda z: -totals[z])


def values(zipcode):
    """Monthly averages for a zipcode (NaN leaves a gap for missing months)."""
    return [series[zipcode].get(m, float("nan")) for m in months]


all_src = ColumnDataSource(dict(x=month_dates, y=values("ALL")))
zip1_src = ColumnDataSource(dict(x=month_dates, y=values(by_volume[0])))
zip2_src = ColumnDataSource(dict(x=month_dates, y=values(by_volume[1])))

select1 = Select(title="Zipcode 1", value=by_volume[0], options=zipcodes)
select2 = Select(title="Zipcode 2", value=by_volume[1], options=zipcodes)

plot = figure(width=800, height=450, x_axis_type="datetime",
              title=f"Monthly average 311 response time, {YEAR}",
              x_axis_label="Month incident was closed",
              y_axis_label="Average create-to-closed time (hours)")
plot.line("x", "y", source=all_src, color="black", line_width=2)
plot.line("x", "y", source=zip1_src, color="royalblue", line_width=2)
plot.line("x", "y", source=zip2_src, color="firebrick", line_width=2)
all_r = plot.renderers[0]
z1_r = plot.renderers[1]
z2_r = plot.renderers[2]
legend = Legend(items=[
    LegendItem(label="All zipcodes", renderers=[all_r]),
    LegendItem(label=f"Zipcode {select1.value}", renderers=[z1_r]),
    LegendItem(label=f"Zipcode {select2.value}", renderers=[z2_r]),
])
plot.add_layout(legend, "right")


def update(attr, old, new):
    zip1_src.data = dict(x=month_dates, y=values(select1.value))
    zip2_src.data = dict(x=month_dates, y=values(select2.value))
    legend.items[1].label = {"value": f"Zipcode {select1.value}"}
    legend.items[2].label = {"value": f"Zipcode {select2.value}"}


select1.on_change("value", update)
select2.on_change("value", update)

curdoc().add_root(column(select1, select2, plot))
curdoc().title = "311 Response Time by Zipcode"
