from uweb3plugins.core.paginators.html_elements import Element
from uweb3plugins.core.paginators.columns import BaseCol
from uweb3plugins.core.paginators import helpers


class MetaTable(type):
    def __new__(cls, name, bases, attrs):
        cls = super().__new__(cls, name, bases, attrs)
        cls._columns = {
            name: obj for name, obj in attrs.items() if isinstance(obj, BaseCol)
        }
        return cls


class BasicTable(metaclass=MetaTable):
    def __init__(self, items):
        self.items = items

    @property
    def render_thead(self):
        return Element(
            "thead",
            children=[
                Element(
                    "tr",
                    children=[
                        Element("th", value=name) for name, col in self._columns.items()
                    ],
                )
            ],
        ).render

    @property
    def render_body(self):
        return Element(
            "tbody",
            children=[
                Element(
                    "tr",
                    children=[col.render(item) for name, col in self._columns.items()],
                )
                for item in self.items
            ],
        ).render
