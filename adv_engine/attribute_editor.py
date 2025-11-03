import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio
from .data_models import Attribute, AttributeGObject

class AttributeEditor(Gtk.Box):
    def __init__(self, attributes):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.append(Gtk.Label(label="Attribute Editor", halign=Gtk.Align.START, css_classes=["title-2"]))

        self.column_view = Gtk.ColumnView()
        self.column_view.set_vexpand(True)

        self.model = Gio.ListStore(item_type=AttributeGObject)
        for attribute in attributes:
            self.model.append(AttributeGObject(attribute))

        self.selection = Gtk.SingleSelection(model=self.model)
        self.column_view.set_model(self.selection)

        self._create_column("ID", lambda attribute: attribute.id)
        self._create_column("Name", lambda attribute: attribute.name)
        self._create_column("Initial Value", lambda attribute: str(attribute.initial_value))
        self._create_column("Max Value", lambda attribute: str(attribute.max_value))

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.column_view)
        self.append(scrolled_window)

    def _create_column(self, title, expression_func):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))
        col = Gtk.ColumnViewColumn(title=title, factory=factory)
        self.column_view.append_column(col)
