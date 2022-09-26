from uweb3plugins.core.paginators.html_elements import Element
from uweb3plugins.core.paginators.columns import BaseCol


def _single_get(item, key):
    try:
        val = item[key]
    except (KeyError, TypeError):
        val = getattr(item, key)

    try:
        return val()
    except TypeError:
        return val


def _recursive_getattr(item, keys):
    try:
        keys = keys.split(".")
    except AttributeError:
        pass

    if item is None:
        return None
    if len(keys) == 1:
        return _single_get(item, keys[0])
    else:
        return _recursive_getattr(_single_get(item, keys[0]), keys[1:])


def _get_attr(item, attr):
    if "." in attr:
        return _recursive_getattr(item, attr)
    else:
        return _single_get(item, attr)


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
                    children=[
                        Element("td", value=_get_attr(item, col.attr))
                        for name, col in self._columns.items()
                    ],
                )
                for item in self.items
            ],
        ).render
