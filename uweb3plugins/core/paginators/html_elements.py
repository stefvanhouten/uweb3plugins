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
        self,
        value,
        attr,
        sort_by,
        sort_direction,
        current_page,
        children: Iterable[Element] | None = None,
        sortable=False,
    ):
        super().__init__(
            name="th",
            value=value,
            children=children,
        )
        if current_page:
            self.url = (
                f"?page={current_page}&sort_by={attr}&sort_direction={sort_direction}"
            )
        else:
            self.url = f"?sort_by={attr}&sort_direction={sort_direction}"

        self.attr = attr
        self.sort_by = sort_by
        self.sort_direction = sort_direction
        self.sortable = sortable

    @property
    def render(self):
        return get_parser().Parse(
            "sortable_head.html",
            element=self,
        )


class TablePagination:
    def __init__(self, table):
        if table.sort_by and table.sort_direction:
            self.sort_url = (
                f"&sort_by={table.sort_by}&sort_direction={table.sort_direction}"
            )
        else:
            self.sort_url = ""

        if table.current_page:
            self.current_page = table.current_page
        else:
            self.current_page = 1

        self.previous_page = max(1, self.current_page - 1)
        self.next_page = self.current_page + 1

        if table.total_pages:
            self.total_pages = table.total_pages
        else:
            self.total_pages = 0
        self.sliding_range = self._sliding_range()

    @property
    def render(self):
        return get_parser().Parse("pagination.html", element=self)

    def _sliding_range(self):
        nav_end = min(self.previous_page + 4, self.total_pages + 1)
        if self.total_pages - self.current_page < 2:
            return range(max(1, self.previous_page - 2), nav_end)
        return range(self.previous_page, nav_end)


class SearchField:
    def __init__(self, table):
        self.table = table

    @property
    def render(self):
        return get_parser().Parse("search_field.html", element=self.table)


class TableHeader:
    def __init__(self, table):
        self.table = table

    @property
    def render(self):
        return Element(
            "thead",
            children=[Element("tr", children=self._get_ths())],
        ).render

    def _get_ths(self) -> list:
        return [
            TableHead(
                current_page=self.table.current_page,
                value=col.name,
                attr=col.attr,
                sortable=col.sortable,
                sort_by=self.table.sort_by,
                sort_direction=self.table.sort_direction,
            )
            for col in self.table._get_columns()
        ]


class TableBody:
    def __init__(self, table):
        self.table = table

    @property
    def render(self):
        return Element(
            "tbody",
            children=[
                Element(
                    "tr",
                    children=[col.render(item) for col in self.table._get_columns()],
                )
                for item in self.table.items
            ],
        ).render


class Table:
    def __init__(self, children):
        self.children = children
        self.initialized_children = []

    def __call__(self, table):
        self.initialized_children = [child(table) for child in self.children]
        return self

    @property
    def render(self):
        return Element("table", children=self.initialized_children).render
