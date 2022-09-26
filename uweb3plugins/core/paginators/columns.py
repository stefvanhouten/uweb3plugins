from uweb3plugins.core.paginators.html_elements import Element
from uweb3plugins.core.paginators import helpers
import string


class MyFormatter(string.Formatter):
    def get_field(self, field_name, args, kwargs):
        return (self.get_value(field_name, args, kwargs), field_name)


class Col:
    def __init__(self, name, attr, sortable=False, enabled=True):
        self.name = name
        self.attr = attr
        self.sortable = sortable
        self.enabled = enabled

    def render(self, item):
        return Element(
            "td", value=helpers.get_attr(item, self.attr)
        )


class LinkCol(Col):
    """
    LinkCol("Test", attr="ID", href="/invoices/{client.name}")
    LinkCol("test2", attr="client.ID", href="/invoices/{title}")
    """

    def __init__(self, name, attr, href, sortable=False):
        super().__init__(name, attr, sortable)
        self.href = href

    def render(self, item):
        field_names = [
            name for text, name, spec, conv in string.Formatter().parse(self.href)
        ]
        url = MyFormatter().vformat(
            self.href, [], {name: helpers.get_attr(item, name) for name in field_names}
        )
        return Element(
            "td",
            children=[
                Element(
                    "a",
                    value=helpers.get_attr(item, self.attr),
                    attrs=f'href="{url}"',
                )
            ],
        )
