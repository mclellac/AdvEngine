import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject

from .data_models import Item

class ItemListModel(GObject.Object, Gtk.ListModel):
    """A Gtk.ListModel implementation for a simple Python list of Item objects."""
    def __init__(self, items):
        super().__init__()
        self.items = items if items is not None else []

    def do_get_item_type(self):
        return Item

    def do_get_n_items(self):
        return len(self.items)

    def do_get_item(self, position):
        return self.items[position]

class ItemEditor(Gtk.Box):
    def __init__(self, items):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        # Title
        self.append(Gtk.Label(label="Item Editor", halign=Gtk.Align.START,
                      css_classes=["title-2"]))

        # --- Column View for Items ---
        self.column_view = Gtk.ColumnView()
        self.column_view.set_vexpand(True)

        # Use the provided item data to create the model
        self.model = ItemListModel(items=items)
        self.selection = Gtk.SingleSelection(model=self.model)
        self.column_view.set_model(self.selection)

        # Define columns
        self._create_column("ID", lambda item: item.id)
        self._create_column("Name", lambda item: item.name)
        self._create_column("Type", lambda item: item.type)
        self._create_column("Buy Price", lambda item: str(item.buy_price))
        self._create_column("Sell Price", lambda item: str(item.sell_price))

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.column_view)

        self.append(scrolled_window)

    def _create_column(self, title, expression_func):
        factory = Gtk.SignalListItemFactory()
        # Setup: Create the widget (a Gtk.Label in this case)
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        # Bind: Connect the data from the item to the widget's properties
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))

        col = Gtk.ColumnViewColumn(title=title, factory=factory)
        self.column_view.append_column(col)
