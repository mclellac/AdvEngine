"""A widget to display search results."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GObject, Gio, Adw

from ..core.schemas.search import SearchResult, SearchResultGObject


class SearchResultsView(Adw.Bin):
    """A widget to display search results in a Gtk.ColumnView.

    This widget takes a list of SearchResult objects and displays them in a
    three-column layout: Type, Name, and ID.
    """

    def __init__(self, **kwargs):
        """Initializes a new SearchResultsView instance."""
        super().__init__(**kwargs)

        self.model = Gio.ListStore(item_type=SearchResultGObject)

        factory_type = Gtk.SignalListItemFactory()
        factory_type.connect("setup", self._on_setup_label)
        factory_type.connect("bind", lambda f, i: self._on_bind_label(f, i, "type"))

        factory_name = Gtk.SignalListItemFactory()
        factory_name.connect("setup", self._on_setup_label)
        factory_name.connect("bind", lambda f, i: self._on_bind_label(f, i, "name"))

        factory_id = Gtk.SignalListItemFactory()
        factory_id.connect("setup", self._on_setup_label)
        factory_id.connect("bind", lambda f, i: self._on_bind_label(f, i, "id"))

        col_type = Gtk.ColumnViewColumn(title="Type", factory=factory_type)
        col_name = Gtk.ColumnViewColumn(title="Name", factory=factory_name)
        col_id = Gtk.ColumnViewColumn(title="ID", factory=factory_id)

        self.column_view = Gtk.ColumnView(model=Gtk.NoSelection(model=self.model))
        self.column_view.append_column(col_type)
        self.column_view.append_column(col_name)
        self.column_view.append_column(col_id)

        scrolled_window = Gtk.ScrolledWindow(
            child=self.column_view, vexpand=True, hexpand=True
        )
        self.set_child(scrolled_window)

    def _on_setup_label(self, factory, list_item):
        """Sets up the label for a list item."""
        label = Gtk.Label()
        list_item.set_child(label)

    def _on_bind_label(self, factory, list_item, property_name):
        """Binds the label to the corresponding property."""
        label = list_item.get_child()
        item = list_item.get_item()
        label.set_text(str(item.get_property(property_name)))
        label.set_halign(Gtk.Align.START)

    def update_results(self, results: list[SearchResult]):
        """Clears the current results and adds the new ones.

        Args:
            results: A list of SearchResult objects.
        """
        self.model.remove_all()
        for result in results:
            self.model.append(
                SearchResultGObject(id=result.id, name=result.name, type=result.type)
            )
