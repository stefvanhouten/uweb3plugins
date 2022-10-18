from __future__ import annotations

import math
from abc import abstractmethod

from uweb3.libs.safestring import HTMLsafestring
from uweb3plugins.core.paginators.columns import Col
from uweb3plugins.core.paginators.html_elements import (
    SearchField,
    Table,
    TableBody,
    TableHeader,
    TablePagination,
)


def get_current_page(get_request_data):
    try:
        return int(get_request_data.getfirst("page", 1))
    except (ValueError, KeyError):
        return 1


def calc_total_pages(total_items: int, items_per_page: int):
    return int(math.ceil(float(total_items) / items_per_page))


class MetaTable(type):
    def __new__(cls, name, bases, attrs):
        cls = super().__new__(cls, name, bases, attrs)
        cls._columns = {
            name: obj for name, obj in attrs.items() if isinstance(obj, Col)
        }
        return cls


class BasicTable(metaclass=MetaTable):
    def __init__(
        self,
        items,
        sort_by=None,
        sort_direction=None,
        search_url=None,
        page=None,
        total_pages=None,
        renderer: None | "RenderCustomTable" = None,
        query: None | str = None,
    ):
        self.items = items
        self.sort_by = sort_by
        self.search_url = search_url
        self.page = page
        self.total_pages = total_pages
        self.query = query

        if not renderer:
            self.renderer = RenderSimpleTable()
        else:
            self.renderer = renderer

        if self.sort_by and not sort_direction:
            # TODO: Warning?
            self.sort_direction = "ASC"
        else:
            self.sort_direction = sort_direction

    def _get_columns(self):
        yield from [col for col in self._columns.values() if col.enabled]

    @property
    def render(self):
        return self.renderer.render(self)


class TableComponents:
    def __init__(self):
        self._components = []

    def add_component(self, component):
        self._components.append(component)

    def render(self, table: BasicTable):
        return HTMLsafestring("").join(
            component(table=table).render for component in self._components
        )


class RenderCustomTable:
    @abstractmethod
    def __init__(self):
        self._renderer = TableComponents()

    def render(self, table: BasicTable):
        return self._renderer.render(table)


class RenderCompleteTable(RenderCustomTable):
    def __init__(self):
        self._renderer = TableComponents()
        self._renderer.add_component(SearchField)
        self._renderer.add_component(
            Table(
                [
                    TableHeader,
                    TableBody,
                ]
            )
        )
        self._renderer.add_component(TablePagination)


class RenderSimpleTable(RenderCustomTable):
    def __init__(self):
        self._renderer = TableComponents()
        self._renderer.add_component(
            Table(
                [
                    TableHeader,
                    TableBody,
                ]
            )
        )
