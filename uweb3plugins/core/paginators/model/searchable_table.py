from typing import Optional

import uweb3

from typing import Type
from uweb3.model import BaseRecord
from uweb3.libs.sqltalk.mysql.connection import Connection
from uweb3plugins.core.paginators import table


class SearchableTableMixin:
    @classmethod
    def IntergratedTable(
        cls: Type[BaseRecord],  # type: ignore
        connection: Connection,
        request_data: uweb3.request.IndexedFieldStorage,
        page_size: int,
        conditions: Optional[list] = None,
        searchable: Optional[list | tuple] = None,
        default_sort: Optional[list[tuple[str, bool]] | None] = None,
    ):

        order = request_data.getfirst("sort_by", None)
        direction = request_data.getfirst("sort_direction", "ASC")
        order_asc = True if direction == "ASC" else False
        page = table.get_current_page(request_data)
        query = request_data.getfirst("query", None)

        if not conditions:
            conditions = []

        if query and searchable:
            conditions.append(
                " OR ".join(
                    [
                        "{name} LIKE {query}".format(
                            name=connection.EscapeField(name),
                            query=connection.EscapeValues(f"%{query}%"),
                        )
                        for name in searchable
                    ]
                )
            )

        data = {
            "offset": max(0, page_size * (page - 1)),
            "limit": page_size,
            "conditions": conditions,
            "yield_unlimited_total_first": True,
        }

        if order:
            data["order"] = [(order, order_asc)]
        if not order and default_sort:
            data["order"] = default_sort

        try:
            results: list[BaseRecord] = list(
                cls.List(
                    connection,
                    **{key: value for key, value in data.items() if value is not None},
                )
            )
        except connection.OperationalError as exc:
            if exc.args[0] == 1054:
                # Unknown column, this should probably be logged.
                pass
            results = []

        try:
            total_items = int(results.pop(0))
        except (IndexError, ValueError):
            total_items = 0

        return results, total_items, page
