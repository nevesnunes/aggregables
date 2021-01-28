#!/usr/bin/env python3

from matplotlib.backends.backend_pdf import PdfPages
from sklearn.cluster import DBSCAN
import argparse
import io
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import re
import statistics
import sys

# From matplotlib's _Set1_data
PALETTE = (
    (0.89411764705882357, 0.10196078431372549, 0.10980392156862745),
    (0.21568627450980393, 0.49411764705882355, 0.72156862745098038),
    (0.30196078431372547, 0.68627450980392157, 0.29019607843137257),
    (0.59607843137254901, 0.30588235294117649, 0.63921568627450975),
    (1.0, 0.49803921568627452, 0.0),
    (1.0, 1.0, 0.2),
    (0.65098039215686276, 0.33725490196078434, 0.15686274509803921),
    (0.96862745098039216, 0.50588235294117645, 0.74901960784313726),
    (0.6, 0.6, 0.6),
)


class BaseStrategy:
    def stdev(self, values):
        if len(values) < 2:
            return 0
        return round(statistics.stdev(values), 2)

    def outlier_detection(self, values):
        # Tukey Fences
        # https://datatest.readthedocs.io/en/stable/how-to/outliers.html
        multiplier = 1.5
        lower = float("inf")
        upper = 0
        sorted_values = sorted(values)
        if len(sorted_values) > 1:
            midpoint = int(round(len(sorted_values) / 2.0))
            q1 = statistics.median(sorted_values[:midpoint])
            q3 = statistics.median(sorted_values[midpoint:])
            iqr = q3 - q1
            lower = q1 - (iqr * multiplier)
            upper = q3 + (iqr * multiplier)
        elif sorted_values:
            lower = upper = sorted_values[0]
        else:
            lower = upper = 0
        outliers = [-1 if x < lower or x > upper else 0 for x in values]
        return outliers, 1, -1


class ClusteringStrategy(BaseStrategy):
    def outlier_detection(self, values):
        X = np.array(values).reshape(-1, 1)

        distances = []
        for a, b in zip(values, values[1:]):
            distances.append(abs(a - b))
        distances = np.sort(distances, axis=0)
        x = distances
        y = [i for i in range(len(distances))]

        # https://stackoverflow.com/questions/16841729/how-do-i-compute-the-derivative-of-an-array-in-python
        # https://stackoverflow.com/questions/52957623/how-to-plot-the-derivative-of-a-plot-python
        dydx = np.diff(y) / np.diff(x)
        if len(dydx) == 0:
            return [-1 for x in values], 0, -1
        pick_dist = np.inf
        pick_i = np.inf
        for i, val in enumerate(dydx):
            candidate_dist = abs(val - 1.0)
            if candidate_dist < pick_dist:
                pick_dist = candidate_dist
                pick_i = i
        if pick_i == np.inf or x[pick_i] <= 0:
            return [-1 for x in values], 0, -1

        eps = x[pick_i]
        m = DBSCAN(eps=eps, min_samples=4)
        m.fit(X)
        clusters = m.labels_
        num_clusters = len(set([x for x in clusters if x > -1]))
        return clusters, num_clusters, eps


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def has_names(line):
    has_names = True
    try:
        if re.match(r'^"\?[0-9]', line):
            has_names = False
    except TypeError:
        if re.compile(b'^"?[0-9]').match(line):
            has_names = False
    return has_names


def color_interpolate(mix=0, c1="#1f77b4", c2="#14466c"):
    """Linear interpolate from color c1 (mix=0) to c2 (mix=1)."""
    if isinstance(c1, str):
        c1 = np.array(mpl.colors.to_rgb(c1))
    else:
        c1 = np.array(c1)
    if isinstance(c2, str):
        c2 = np.array(mpl.colors.to_rgb(c2))
    else:
        c2 = np.array(c2)
    return mpl.colors.to_hex((1 - mix) * c1 + mix * c2)


def record_color(cardinality, record, value, min_value, max_value):
    if record == -1:
        return color_interpolate(mix=0, c1=PALETTE[record])
    if cardinality < 2:
        return color_interpolate((value - min_value) / (max_value - min_value))
    elif cardinality < 8:
        return color_interpolate(mix=0, c1=PALETTE[record])
    return color_interpolate()


def make_bars(measures, comparisons, min_value, max_value):
    fig = plt.figure()
    for j in range(measures["subplot_count"]):
        comparisons_i = (measures["subplot_count"] * measures["subplot_i"]) + j
        if comparisons_i > len(comparisons) - 1:
            break
        values = comparisons[comparisons_i]["values"]
        ax = fig.add_subplot(
            math.ceil(measures["subplot_count"] / measures["n_cols"]),
            measures["n_cols"],
            j + 1,
        )
        b = ax.bar(measures["br"], values, measures["width"], align="center")
        for k, value in enumerate(values):
            b[k].set_color(
                record_color(
                    comparisons[comparisons_i]["cardinality"],
                    comparisons[comparisons_i]["records"][k],
                    value,
                    min_value,
                    max_value,
                )
            )

        name = comparisons[comparisons_i]["name"]
        if len(name) > 64:
            name = name[0:8] + "…" + name[-(64 - 8) :]

        eps_label = ""
        eps = comparisons[comparisons_i]["eps"]
        if eps > -1:
            eps_label = f", eps: {round(eps, 4)}"

        ax.set_title(
            f'{name}\noutliers: {comparisons[comparisons_i]["outlier_factor"]}, stdev: {comparisons[comparisons_i]["normalized_stdev"]} ({comparisons[comparisons_i]["stdev"]}), #: {comparisons[comparisons_i]["cardinality"]}{eps_label}',
            fontsize="medium",
        )
    fig.tight_layout()
    return fig


def parse_request():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--filename", type=str, help="Path for csv file",
    )
    parser.add_argument(
        "-o",
        "--output-filename",
        const="out",
        nargs="?",
        type=str,
        help="Path for output pdf file",
    )
    parser.add_argument(
        "-s",
        "--strategy",
        type=str,
        default="tukey_fences",
        const="tukey_fences",
        nargs="?",
        choices=["tukey_fences", "clustering"],
        help="Strategy for calculating outliers",
    )
    parsed_args = parser.parse_args()

    contents = None
    if not sys.stdin.isatty():
        raw_contents = sys.stdin.read()
        first_line = raw_contents.split("\n")[0]
        contents = io.StringIO(raw_contents)
    else:
        with open(parsed_args.filename, "rb") as f:
            first_line = f.readline()
        contents = parsed_args.filename
    data = np.genfromtxt(
        contents,
        filling_values=np.inf,
        delimiter=",",
        names=has_names(first_line),
        deletechars="",
    )

    if parsed_args.strategy == "clustering":
        strategy = ClusteringStrategy()
    else:
        strategy = BaseStrategy()

    return data, strategy, parsed_args.output_filename


if __name__ == "__main__":
    data, strategy, output_filename = parse_request()

    var_count = len(data.dtype.names)
    min_value = float("inf")
    max_value = 0
    comparisons = []
    for i in range(var_count):
        name = data.dtype.names[i]
        values_with_filling = data[name]
        values_no_filling = [x for x in values_with_filling if x != np.inf]
        values = [x if x != np.inf else -1.0 for x in values_with_filling]
        if len(values_no_filling) == 0:
            values_no_filling = values[:]

        local_max_value = max(values_no_filling)
        if local_max_value > max_value:
            max_value = local_max_value
        local_min_value = min(values_no_filling)
        if local_min_value < min_value:
            min_value = local_min_value

        stdev = strategy.stdev(values_no_filling)
        local_value_range = abs(local_max_value - local_min_value)
        if local_value_range == 0:
            normalized_stdev = 0
        else:
            normalized_stdev = round(stdev / abs(local_max_value - local_min_value), 4)

        records, cardinality, eps = strategy.outlier_detection(values_no_filling)
        outlier_factor = len([x for x in records if x == -1])
        records_with_filling = []
        r_i = 0
        for val in values_with_filling:
            if val == np.inf:
                records_with_filling.append(-1)
            else:
                records_with_filling.append(records[r_i])
                r_i += 1

        comparisons.append(
            {
                "cardinality": cardinality,
                "eps": eps,
                "name": name,
                "normalized_stdev": normalized_stdev,
                "outlier_factor": outlier_factor,
                "records": records_with_filling,
                "stdev": stdev,
                "values": values,
            }
        )
    comparisons = sorted(
        comparisons,
        key=lambda x: (
            x["cardinality"],
            1 / x["eps"],
            x["outlier_factor"],
            x["normalized_stdev"],
        ),
        reverse=True,
    )

    subplot_count = 3
    n_cols = 1
    width = 0.75
    measures = {
        "subplot_count": subplot_count,
        "n_cols": n_cols,
        "n_rows": var_count / n_cols + 1,
        "width": width,
        "br": np.arange(0, len(data[data.dtype.names[0]]) - width),
    }
    comparisons_chunked = list(chunks(comparisons, subplot_count))
    if True:
        # if var_count > subplot_count:
        pdf = PdfPages(f"{output_filename}.pdf")
        for i in range(len(comparisons_chunked)):
            measures["subplot_i"] = i
            fig = make_bars(measures, comparisons, min_value, max_value)
            pdf.savefig(fig)
        pdf.close()
    else:
        measures["subplot_i"] = 0
        make_bars(measures, comparisons, min_value, max_value)
        plt.show()
