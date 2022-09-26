import os
from typing import Iterable

from uweb3.templateparser import Parser


def get_parser():
    return Parser(path=os.path.join(os.path.dirname(__file__), "templates"))


class Element:
    def __init__(
        self,
        name,
        value=None,
        attrs=None,
        children: Iterable["Element"] | None = None,
    ):
        self.name = name
        self.value = value
        self.attrs = attrs
        self.children = children

    @property
    def render(self):
        return get_parser().Parse(
            "element.html",
            element=self,
        )


class TableHead(Element):
    def __init__(
        self, value, children: Iterable[Element] | None = None, sortable=False
    ):
        super().__init__(
            name="th",
            value=value,
            children=children,
        )
        self.sortable = sortable

    @property
    def render(self):
        return get_parser().Parse(
            "sortable_head.html",
            element=self,
        )
