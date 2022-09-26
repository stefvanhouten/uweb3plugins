from uweb3plugins.core.paginators.html_elements import Element
from uweb3plugins.core.paginators import helpers
import string


class MyFormatter(string.Formatter):
    def get_field(self, field_name, args, kwargs):
        return (self.get_value(field_name, args, kwargs), field_name)


class Col:
    def __init__(self, name, attr, sortable=False, enabled=True):
        """Base column class that can be used to render simple
        columns in a table.

        Args:
            name (str): The title of the column, this will be displayed
                in the <th> element.
            attr (str): The attribute name of the value that should be
                retrieved from the item. When the item has nested children
                (because of lazyloading) or the item is a dict with nested
                keys the following syntax can be used to extract the value
                from a nested object: "foo.bar.baz". This will return the
                value of item["foo"]["bar"]["baz"].
            sortable (bool, optional): Determines if the column is sortable.
                Defaults to False.
            enabled (bool, optional): Determine wheter or not
                this column header and value should be displayed.
                Defaults to True.

        Example usage:
            class Items:
                ID: int
                name: str

            class ItemsTable(BasicTable):
                id = Col("ID", attr="ID")
                name = Col("Name", attr="name")

            table = ItemsTable(items=[Items(ID=1, name="foo"), Items(ID=2, name="bar")])

            The rendered table will look like this:
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>1</td>
                            <td>foo</td>
                        </tr>
                        <tr>
                            <td>2</td>
                            <td>bar</td>
                        </tr>
                    </tbody>
                </table>

        """
        self.name = name
        self.attr = attr
        self.sortable = sortable
        self.enabled = enabled

    def render(self, item):
        return Element("td", value=helpers.get_attr(item, self.attr))


class LinkCol(Col):
    def __init__(self, name, attr, href, *args, **kwargs):
        """Adds a row to the table of the following format:
            <td>
                <a href="href">attr</a>
            </td>

        The value that is displayed is the passed attr value.
        The column will be populated with data on render, the
        value in the href will be retrieved from the current item
        that is being iterated over.

        Retrival of nested values or children from uweb3 model
        objects is supported. For example if we have a record
        class that looks like this:

            class Client(uweb3.model.Record):
                ID: int
                name: str

            class Invoice(uweb3.model.Record):
                ID: int
                title: str
                client: Client.ID

            class Table(BasicTable):
                col1 = LinkCol("Client", attr="client.name", href="/client/{client.ID}")
                col2 = LinkCol("Invoice", attr="title", href="/invoices/{ID}")

            Table(items=[Invoice(1, "Invoice 1", Client(1, "Client 1"))])

            The rendered table will look like this:
                <table>
                    <thead>
                        <tr>
                            <th>Client</th>
                            <th>Invoice</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>
                                <a href="/client/1">Client 1</a>
                            </td>
                            <td>
                                <a href="/invoices/1">Invoice 1</a>
                            </td>
                        </tr>
                    </tbody>
                </table>

        It is also possible to pass an href without any fields:
            class Table(BasicTable):
                LinkCol("Invoice", attr="title", href="/invoices")

            which will result in the following table:
                <table>
                    <thead>
                        <tr>
                            <th>Invoice</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>
                                <a href="/invoices">Invoice 1</a>
                            </td>
                        </tr>
                    </tbody>
                </table>
        """
        super().__init__(name, attr, *args, **kwargs)
        self.href = href

    def render(self, item):
        # Retrieve all fields that should be replaced in the href.
        # When no {replacements} are found just use the href as is.
        field_names = [
            name
            for text, name, spec, conv in string.Formatter().parse(self.href)
            if name
        ]
        # This is some fuckery that allows formatting replacements like
        # {replacement.key}, normally this is not allowed because
        # dot syntax is not supported in fstrings. This is a workaround.
        formatted_url = MyFormatter().vformat(
            self.href, [], {name: helpers.get_attr(item, name) for name in field_names}
        )
        return Element(
            "td",
            children=[
                Element(
                    "a",
                    value=helpers.get_attr(item, self.attr),
                    attrs=f'href="{formatted_url}"',
                )
            ],
        )
