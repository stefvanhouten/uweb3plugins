from uweb3plugins.core.paginators.html_elements import Element, TableHead
from uweb3plugins.core.paginators.columns import Col


class MetaTable(type):
    def __new__(cls, name, bases, attrs):
        cls = super().__new__(cls, name, bases, attrs)
        cls._columns = {
            name: obj for name, obj in attrs.items() if isinstance(obj, Col)
        }
        return cls


class BasicTable(metaclass=MetaTable):
    def __init__(self, items, sort_by=None, sort_direction=None):
        self.items = items
        self.sort_by = sort_by

        if self.sort_by and not sort_direction:
            # TODO: Warning?
            self.sort_direction = "ASC"
        else:
            self.sort_direction = sort_direction

    def _get_columns(self):
        yield from [col for col in self._columns.values() if col.enabled]

    @property
    def render_thead(self):
        return Element(
            "thead",
            children=[
                Element(
                    "tr",
                    children=[
                        TableHead(
                            value=col.name,
                            sortable=col.sortable,
                            sort_by=self.sort_by,
                            sort_direction=self.sort_direction,
                        )
                        for col in self._get_columns()
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
                    children=[col.render(item) for col in self._get_columns()],
                )
                for item in self.items
            ],
        ).render
