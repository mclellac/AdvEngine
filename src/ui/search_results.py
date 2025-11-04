import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GObject, Gio

from ..core.data_schemas import SearchResultGObject


class SearchResultsView(Gtk.Box):
    """A widget to display search results in a Gtk.ColumnView."""

    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)

        self.model = Gio.ListStore(item_type=SearchResultGObject)

        # Factory for the 'Type' column
        factory_type = Gtk.SignalListItemFactory()
        factory_type.connect("setup", self._on_setup_label)
        factory_type.connect("bind", lambda f, i: self._on_bind_label(f, i, "type"))

        # Factory for the 'Name' column
        factory_name = Gtk.SignalListItemFactory()
        factory_name.connect("setup", self._on_setup_label)
        factory_name.connect("bind", lambda f, i: self._on_bind_label(f, i, "name"))

        # Factory for the 'ID' column
        factory_id = Gtk.SignalListItemFactory()
        factory_id.connect("setup", self._on_setup_label)
        factory_id.connect("bind", lambda f, i: self._on_bind_label(f, i, "id"))

        # Type Column
        col_type = Gtk.ColumnViewColumn(title="Type", factory=factory_type)
        col_type.set_expand(False)

        # Name Column
        col_name = Gtk.ColumnViewColumn(title="Name", factory=factory_name)
        col_name.set_expand(True)

        # ID Column
        col_id = Gtk.ColumnViewColumn(title="ID", factory=factory_id)
        col_id.set_expand(True)

        self.column_view = Gtk.ColumnView(model=Gtk.NoSelection(model=self.model))
        self.column_view.append_column(col_type)
        self.column_view.append_column(col_name)
        self.column_view.append_column(col_id)

        scrolled_window = Gtk.ScrolledWindow(
            child=self.column_view, vexpand=True, hexpand=True
        )
        self.append(scrolled_window)

    def _on_setup_label(self, factory, list_item):
        """Set up the label for a list item."""
        label = Gtk.Label()
        list_item.set_child(label)

    def _on_bind_label(self, factory, list_item, property_name):
        """Bind the label to the corresponding property in the SearchResultGObject."""
        label = list_item.get_child()
        item = list_item.get_item()
        label.set_text(str(item.get_property(property_name)))
        label.set_halign(Gtk.Align.START)

    def update_results(self, results):
        """Clears the current results and adds the new ones."""
        self.model.remove_all()
        for result in results:
            self.model.append(
                SearchResultGObject(
                    id=result.id, name=result.name, type=result.type
                )
            )
