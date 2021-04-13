#!/usr/bin/env python3

from category_index import ReverseIndex

DATA = [
    {
        "title": "Django",
        "description": "Django is a high-level Python Web framework that "
        "encourages rapid development and clean, pragmatic design.  Built by "
        "experienced developers, it takes care of much of the hassle of Web "
        "development, so you can focus on writing your app without needing to "
        "reinvent the wheel. It’s free and open source.",
    },
    {
        "title": "Python",
        "description": "Python is a programming language that lets you work "
        "more quickly and integrate your systems more effectively.",
    },
]
SYNONYMS = {
    "rapid": "quick",
}
index = ReverseIndex(DATA, SYNONYMS, fields=["title", "description"])
print(index.index)
print(list(index.query("Python")))
print(list(index.query("Python", fields=["title"])))
print(list(index.query("python", fields=["description"])))
print(list(index.query("Python web")))
print(list(index.query("Python web", "OR")))
print(list(index.query("quick")))
print(list(index.query("rapid")))
print(list(index.query("of")))
