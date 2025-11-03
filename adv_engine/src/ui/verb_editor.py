import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw
from ..core.data_schemas import Verb, VerbGObject

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, Gdk
from ..core.data_schemas import Verb, VerbGObject

class VerbEditorDialog(Adw.MessageDialog):
    def __init__(self, parent, project_manager, verb=None):
        super().__init__(transient_for=parent, modal=True)
        self.set_heading("Add New Verb" if verb is None else "Edit Verb")
        self.project_manager = project_manager
        self.verb = verb

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        .error {
            border: 1px solid red;
            border-radius: 6px;
        }
        """)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)
        self.set_extra_child(content)

        self.id_entry = Gtk.Entry(text=verb.id if verb else "")
        self.name_entry = Gtk.Entry(text=verb.name if verb else "")

        content.append(self._create_row("ID:", self.id_entry))
        content.append(self._create_row("Name:", self.name_entry))

        self.add_response("cancel", "_Cancel")
        self.add_response("ok", "_OK")
        self.set_default_response("ok")
        self.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)

        self.id_entry.connect("changed", self._validate)
        self.name_entry.connect("changed", self._validate)
        self._validate(None)

    def _validate(self, entry):
        is_valid = True
        id_text = self.id_entry.get_text()
        is_new_verb = self.verb is None
        id_is_duplicate = any(v.id == id_text for v in self.project_manager.data.verbs if (is_new_verb or v.id != self.verb.id))

        if not id_text or id_is_duplicate:
            self.id_entry.add_css_class("error")
            if not id_text:
                self.id_entry.set_tooltip_text("ID cannot be empty.")
            else:
                self.id_entry.set_tooltip_text("This ID is already in use.")
            is_valid = False
        else:
            self.id_entry.remove_css_class("error")
            self.id_entry.set_tooltip_text("")

        if not self.name_entry.get_text():
            self.name_entry.add_css_class("error")
            self.name_entry.set_tooltip_text("Name cannot be empty.")
            is_valid = False
        else:
            self.name_entry.remove_css_class("error")
            self.name_entry.set_tooltip_text("")

        self.set_response_enabled("ok", is_valid)

    def _create_row(self, label_text, widget):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label = Gtk.Label(label=label_text, halign=Gtk.Align.START, hexpand=True)
        box.append(label)
        box.append(widget)
        return box

class VerbEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.project_manager = project_manager

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, hexpand=True, vexpand=True)
        self.append(self.main_box)

        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title = Gtk.Label(label="Verb Editor", halign=Gtk.Align.START, hexpand=True, css_classes=["title-2"])
        header_box.append(title)

        toolbar = Gtk.Box(spacing=5)
        self.add_button = Gtk.Button(label="Add")
        self.add_button.connect("clicked", self._on_add_clicked)
        self.edit_button = Gtk.Button(label="Edit")
        self.edit_button.connect("clicked", self._on_edit_clicked)
        self.delete_button = Gtk.Button(label="Delete")
        self.delete_button.connect("clicked", self._on_delete_clicked)

        toolbar.append(self.add_button)
        toolbar.append(self.edit_button)
        toolbar.append(self.delete_button)
        header_box.append(toolbar)
        self.main_box.append(header_box)

        self.column_view = Gtk.ColumnView()
        self.column_view.set_vexpand(True)

        self.model = Gio.ListStore(item_type=VerbGObject)
        for verb in self.project_manager.data.verbs:
            self.model.append(VerbGObject(verb))

        self.selection = Gtk.SingleSelection(model=self.model)
        self.column_view.set_model(self.selection)

        self._create_column("ID", Gtk.StringSorter(), lambda verb: verb.id)
        self._create_column("Name", Gtk.StringSorter(), lambda verb: verb.name)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.column_view)
        self.main_box.append(scrolled_window)

    def _create_column(self, title, sorter, expression_func):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))

        col = Gtk.ColumnViewColumn(title=title, factory=factory, sorter=sorter)
        self.column_view.append_column(col)

    def _on_add_clicked(self, button):
        dialog = VerbEditorDialog(self.get_root(), self.project_manager)
        dialog.connect("response", self._on_add_dialog_response)
        dialog.present()

    def _on_add_dialog_response(self, dialog, response):
        if response == "ok":
            new_verb = self.project_manager.add_verb(
                id=dialog.id_entry.get_text(),
                name=dialog.name_entry.get_text()
            )
            self.model.append(VerbGObject(new_verb))
        dialog.destroy()

    def _on_edit_clicked(self, button):
        selected_verb_gobject = self.selection.get_selected_item()
        if selected_verb_gobject:
            dialog = VerbEditorDialog(self.get_root(), self.project_manager, verb=selected_verb_gobject.verb_data)
            dialog.connect("response", self._on_edit_dialog_response, selected_verb_gobject)
            dialog.present()

    def _on_edit_dialog_response(self, dialog, response, verb_gobject):
        if response == "ok":
            verb_gobject.verb_data.id = dialog.id_entry.get_text()
            verb_gobject.verb_data.name = dialog.name_entry.get_text()
            self.project_manager.set_dirty(True)
            pos = self.model.find(verb_gobject)[1]
            if pos >= 0:
                self.model.items_changed(pos, 1, 1)
        dialog.destroy()

    def _on_delete_clicked(self, button):
        selected_verb_gobject = self.selection.get_selected_item()
        if selected_verb_gobject:
            dialog = Adw.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                heading="Delete Verb?",
                body=f"Are you sure you want to delete '{selected_verb_gobject.name}'?"
            )
            dialog.add_response("cancel", "_Cancel")
            dialog.add_response("delete", "_Delete")
            dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.connect("response", self._on_delete_dialog_response, selected_verb_gobject)
            dialog.present()

    def _on_delete_dialog_response(self, dialog, response, verb_gobject):
        if response == "delete":
            self.project_manager.data.verbs.remove(verb_gobject.verb_data)
            self.project_manager.set_dirty()
            pos = self.model.find(verb_gobject)[1]
            if pos >= 0:
                self.model.remove(pos)
        dialog.destroy()
