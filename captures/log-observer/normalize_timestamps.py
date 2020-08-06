#!/usr/bin/env python3

import datetime
import re
import sys

formats = [
    {
        "datetime": "%d %b %Y %H:%M:%S,%f",
        "regex": r"[0-9]{2} \w{3} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]+",
    },
    {
        "datetime": "%d %b %Y %H:%M:%S,%f",
        "regex": r"[0-9]{2} \w{3} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+",
    },
    {
        "datetime": "%d-%b-%Y %H:%M:%S,%f",
        "regex": r"[0-9]{2}-\w{3}-[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]+",
    },
    {
        "datetime": "%d-%b-%Y %H:%M:%S.%f",
        "regex": r"[0-9]{2}-\w{3}-[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+",
    },
    {
        "datetime": "%Y-%m-%d %H:%M:%S,%f",
        "regex": r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]+",
    },
    {
        "datetime": "%d/%b/%Y:%H:%M:%S",
        "regex": r"[0-9]{2}/\w{3}/[0-9]{4}:[0-9]{2}:[0-9]{2}:[0-9]{2}",
    },
]

normalized_format = "%Y-%m-%d %H:%M:%S.%f"

def normalize(line):
    subs = []
    for format in formats:
        matches = re.findall(format["regex"], line)
        for match in matches:
            match_datetime = datetime.datetime.strptime(match, format["datetime"])
            subs.append(match_datetime.strftime(normalized_format))
    return subs

def date(line):
    return datetime.datetime.strptime(normalize(line)[0], normalized_format)
