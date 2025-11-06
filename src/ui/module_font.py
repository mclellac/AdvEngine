import os
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, Pango
from ..core.data_schemas import Font, FontGObject

class FontManager(Adw.Bin):
    EDITOR_NAME = "Fonts"
    VIEW_NAME = "font_manager"
    ORDER = 11

    def __init__(self, project_manager, **kwargs):
        super().__init__(**kwargs)
        self.project_manager = project_manager

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        self.set_child(main_box)

        # Font List
        self.font_list = Gtk.ColumnView()
        self.font_list.set_vexpand(True)
        self.model = Gio.ListStore(item_type=FontGObject)
        for font in self.project_manager.data.fonts:
            self.model.append(FontGObject(font))

        self.selection = Gtk.SingleSelection(model=self.model)
        self.font_list.set_model(self.selection)

        self._create_column("ID", Gtk.StringSorter(), lambda font: font.id)
        self._create_column("Name", Gtk.StringSorter(), lambda font: font.name)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.font_list)

        self.status_page = Adw.StatusPage(title="No Fonts", icon_name="font-x-generic-symbolic")

        self.main_stack = Gtk.Stack()
        self.main_stack.add_named(scrolled_window, "list")
        self.main_stack.add_named(self.status_page, "status")
        main_box.append(self.main_stack)

        # Font Preview
        self.font_preview = Gtk.Label(label="The quick brown fox jumps over the lazy dog")
        self.font_preview.set_hexpand(True)
        main_box.append(self.font_preview)

        self.selection.connect("selection-changed", self._on_font_selected)
        self._on_font_selected(self.selection, None)

        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        add_button = Gtk.Button(label="Add Font")
        add_button.connect("clicked", self._on_add_font)
        button_box.append(add_button)

        delete_button = Gtk.Button(label="Delete Font")
        delete_button.connect("clicked", self._on_delete_font)
        button_box.append(delete_button)
        main_box.append(button_box)

        self._update_visibility()

    def _update_visibility(self):
        has_fonts = self.model.get_n_items() > 0
        if has_fonts:
            self.main_stack.set_visible_child_name("list")
        else:
            self.main_stack.set_visible_child_name("status")

    def _create_column(self, title, sorter, expression_func):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))

        col = Gtk.ColumnViewColumn(title=title, factory=factory, sorter=sorter)
        self.font_list.append_column(col)

    def _on_font_selected(self, selection, _):
        selected_font = selection.get_selected_item()
        if selected_font:
            self._display_font_preview(selected_font)
        else:
            self._clear_font_preview()

    def _display_font_preview(self, font):
        self.font_preview.set_attributes(Pango.AttrList.from_string(f"{{font_family: '{font.name}'}}"))

    def _clear_font_preview(self):
        self.font_preview.set_attributes(None)

    def _on_add_font(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Add Font",
            parent=self.get_root(),
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL, "_Ok", Gtk.ResponseType.OK
        )

        def on_dialog_response(dialog, response):
            if response == Gtk.ResponseType.OK:
                file = dialog.get_file()
                file_path = file.get_path()
                font_name = os.path.basename(file_path)
                new_font = self.project_manager.add_font(id=f"font_{len(self.model) + 1}", name=font_name, file_path=file_path)
                self.model.append(FontGObject(new_font))
            dialog.destroy()

        dialog.connect("response", on_dialog_response)
        dialog.show()

    def _on_delete_font(self, button):
        selected_font = self.selection.get_selected_item()
        if selected_font:
            self.project_manager.remove_font(selected_font.id)
            for i, item in enumerate(self.model):
                if item.id == selected_font.id:
                    self.model.remove(i)
                    break
