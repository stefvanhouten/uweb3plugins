from typing import Optional

import uweb3

from uweb3.model import BaseRecord
from uweb3.libs.sqltalk.mysql.connection import Connection
from uweb3plugins.core.paginators import table


class SearchableTableMixin:
    @classmethod
    def IntergratedTable(
        cls: BaseRecord,  # type: ignore
        connection: Connection,
        request_data: uweb3.request.IndexedFieldStorage,
        page_size: int,
        conditions: Optional[list] = None,
        searchable: Optional[list | tuple] = None,
    ):

        order = request_data.getfirst("sort_by", None)
        direction = request_data.getfirst("sort_direction", "ASC")
        order_asc = True if direction == "ASC" else False
        current_page = table.get_current_page(request_data)
        query = request_data.getfirst("query", None)

        if not conditions:
            conditions = []

        if query and searchable:
            conditions.append(
                " OR ".join(
                    [
                        "`{name}` LIKE '%{query}%'".format(
                            name=name, query=connection.EscapeValues(query)[1:-1]
                        )
                        for name in searchable
                    ]
                )
            )
        data = {
            "order": [(order, order_asc)] if order else None,
            "offset": max(0, page_size * (current_page - 1)),
            "limit": page_size,
            "conditions": conditions,
            "yield_unlimited_total_first": True,
        }

        results = cls.List(
            connection,
            **{key: value for key, value in data.items() if value is not None},
        )

        try:
            total_items = int(results.pop(0))
        except (IndexError, ValueError):
            total_items = 0

        return results, total_items, current_page
