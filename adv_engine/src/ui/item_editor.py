import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio
from ..core.data_schemas import ItemGObject

class ItemEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.project_manager = project_manager

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

        self.model = Gio.ListStore(item_type=ItemGObject)
        for item in self.project_manager.data.items:
            self.model.append(ItemGObject(item))

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
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))

        col = Gtk.ColumnViewColumn(title=title, factory=factory)
        self.column_view.append_column(col)
