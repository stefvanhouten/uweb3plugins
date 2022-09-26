import os
from typing import Iterable

from uweb3.templateparser import Parser


def get_parser():
    return Parser(path=os.path.join(os.path.dirname(__file__), "templates"))


class Element:
    def __init__(
        self, name, value=None, attrs=None, children: Iterable["Element"] | None = None
    ):
        self.name = name
        self.value = value
        self.attrs = attrs
        self.children = children

    @property
    def render(self):
        return get_parser().Parse(
            "/home/stef/devel/uweb3plugins/uweb3plugins/core/paginators/templates/element.html",
            element=self,
        )
