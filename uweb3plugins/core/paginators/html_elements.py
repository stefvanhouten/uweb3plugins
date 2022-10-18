import os
from typing import Iterable

import urllib.parse
from uweb3.templateparser import Parser


def get_parser():
    return Parser(path=os.path.join(os.path.dirname(__file__), "templates"))


def build_url(table, keys):
    query_args = {}

    for key in keys:
        default = None
        needle = key
        
        if isinstance(key, tuple):
            needle = key[0]
            default = key[1]

        value = getattr(table, needle)
        
        if value:
            query_args[needle] = value
        elif default:
            query_args[needle] = default
    return urllib.parse.urlencode(query_args)


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
        table,
        col,
        children: Iterable[Element] | None = None,
    ):
        super().__init__(
            name="th",
            value=col.name,
            children=children,
        )

        url = build_url(
            table,
            (
                ("page", 1),
                ("sort_by", col.attr),
                "query",
            ),
        )
        self.url = f"?{url}"
        self.attr = col.attr
        self.sort_by = table.sort_by
        self.sort_direction = table.sort_direction
        self.sortable = col.sortable

    @property
    def render(self):
        return get_parser().Parse(
            "sortable_head.html",
            element=self,
        )


class TablePagination:
    def __init__(self, table):
        self.sort_url = "&" + build_url(
            table,
            (
                "sort_by",
                "sort_direction",
                "query",
            ),
        )

        if table.page:
            self.page = table.page
        else:
            self.page = 1

        self.previous_page = max(1, self.page - 1)
        self.next_page = self.page + 1

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
        if self.total_pages - self.page < 2:
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
        return [TableHead(self.table, col) for col in self.table._get_columns()]


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
