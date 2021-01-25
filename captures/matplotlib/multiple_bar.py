#!/usr/bin/env python3

from enum import Enum
import io
import math
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import re
import sys
import statistics


def color_interpolate(c1, c2, mix=0):
    """Linear interpolate from color c1 (mix=0) to c2 (mix=1)."""
    c1 = np.array(mpl.colors.to_rgb(c1))
    c2 = np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1 - mix) * c1 + mix * c2)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


OutlierStrategy = Enum("OutlierStrategy", "stdev tukey_fences")
outlier_strategy = OutlierStrategy.tukey_fences


def outlier_factor(values, strategy=outlier_strategy):
    if strategy == OutlierStrategy.tukey_fences:
        # https://datatest.readthedocs.io/en/stable/how-to/outliers.html
        multiplier = 1.5
        lower = float("inf")
        upper = 0
        values = sorted(values)
        if len(values) >= 2:
            midpoint = int(round(len(values) / 2.0))
            q1 = statistics.median(values[:midpoint])
            q3 = statistics.median(values[midpoint:])
            iqr = q3 - q1
            lower = q1 - (iqr * multiplier)
            upper = q3 + (iqr * multiplier)
        elif values:
            lower = upper = values[0]
        else:
            lower = upper = 0
        outliers = [x for x in values if x < lower or x > upper]
        return len(outliers)
    else:
        if len(values) < 2:
            return 0
        return round(statistics.stdev(values), 2)


if __name__ == "__main__":
    has_names = True
    contents = None
    if not sys.stdin.isatty():
        raw_contents = sys.stdin.read()
        first_line = raw_contents.split("\n")[0]
        contents = io.StringIO(raw_contents)
    else:
        with open(sys.argv[1], "rb") as f:
            first_line = f.readline()
        contents = sys.argv[1]
    try:
        if re.match(r'^"\?[0-9]', first_line):
            has_names = False
    except TypeError:
        if re.compile(b'^"?[0-9]').match(first_line):
            has_names = False
    data = np.genfromtxt(
        contents, filling_values=np.inf, delimiter=",", names=has_names, deletechars=""
    )

    var_count = len(data.dtype.names)
    min_value = float("inf")
    max_value = 0
    comparisons = []
    for i in range(var_count):
        name = data.dtype.names[i]
        values = data[data.dtype.names[i]]
        values_no_filling = [x for x in values if x != np.inf]
        values = [x if x != np.inf else -1.0 for x in values]
        if len(values_no_filling) == 0:
            values_no_filling = values[:]
        local_max_value = max(values_no_filling)
        if local_max_value > max_value:
            max_value = local_max_value
        local_min_value = min(values_no_filling)
        if local_min_value < min_value:
            min_value = local_min_value
        stdev = outlier_factor(values_no_filling, OutlierStrategy.stdev)
        local_value_range = abs(local_max_value - local_min_value)
        if local_value_range == 0:
            normalized_stdev = 0
        else:
            normalized_stdev = round(stdev / abs(local_max_value - local_min_value), 4)
        comparisons.append(
            {
                "name": name,
                "outlier_factor": outlier_factor(values_no_filling),
                "stdev": stdev,
                "normalized_stdev": normalized_stdev,
                "values": values,
            }
        )
    comparisons = sorted(
        comparisons,
        key=lambda x: (x["outlier_factor"], x["normalized_stdev"]),
        reverse=True,
    )

    def make_bars(subplot_count, i, comparisons):
        fig = plt.figure()
        for j in range(subplot_count):
            comparisons_i = (subplot_count * i) + j
            if comparisons_i > len(comparisons) - 1:
                break
            values = comparisons[comparisons_i]["values"]
            ax = fig.add_subplot(math.ceil(subplot_count / n_cols), n_cols, j + 1)
            b = ax.bar(br, values, width, align="center")
            for j, value in enumerate(values):
                b[j].set_color(
                    color_interpolate(
                        min_color,
                        max_color,
                        (value - min_value) / (max_value - min_value),
                    )
                )
            label = comparisons[comparisons_i]["name"]
            if len(label) > 64:
                label = label[0:8] + "…" + label[-(64 - 8) :]
            ax.set_title(
                f'{label}\noutliers: {comparisons[comparisons_i]["outlier_factor"]}, stdev: {comparisons[comparisons_i]["normalized_stdev"]} ({comparisons[comparisons_i]["stdev"]})'
            )
        fig.tight_layout()
        return fig

    min_color = "#1f77b4"
    max_color = "#14466c"
    # subplot_count = 6
    # n_cols = 2
    subplot_count = 3
    n_cols = 1
    n_rows = var_count / n_cols + 1
    width = 0.75
    a = data[data.dtype.names[0]]
    br = np.arange(0, len(a) - width)

    comparisons_chunked = list(chunks(comparisons, subplot_count))
    if var_count > subplot_count:
        pdf = PdfPages("out.pdf")
        for i in range(len(comparisons_chunked)):
            fig = make_bars(subplot_count, i, comparisons)
            pdf.savefig(fig)
        pdf.close()
    else:
        make_bars(subplot_count, 0, comparisons)
        plt.show()
