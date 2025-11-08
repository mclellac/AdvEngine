import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw
from ..core.data_schemas import UILayout, UIElement, UILayoutGObject

class UIBuilder(Adw.Bin):
    EDITOR_NAME = "UI Builder"
    VIEW_NAME = "ui_builder"
    ORDER = 10

    def __init__(self, **kwargs):
        print("DEBUG: UIBuilder.__init__")
        project_manager = kwargs.pop('project_manager')
        settings_manager = kwargs.pop('settings_manager')
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.settings_manager = settings_manager
        self.active_layout = None
        self.active_element = None

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        self.set_child(main_box)

        # UI Layout List
        self.layout_list = Gtk.ColumnView()
        self.layout_list.set_vexpand(True)
        self.model = Gio.ListStore(item_type=UILayoutGObject)
        for layout in self.project_manager.data.ui_layouts:
            self.model.append(UILayoutGObject(layout))

        self.selection = Gtk.SingleSelection(model=self.model)
        self.layout_list.set_model(self.selection)

        self._create_column("ID", lambda layout: layout.id)
        self._create_column("Name", lambda layout: layout.name)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.layout_list)

        self.status_page = Adw.StatusPage(title="No UI Layouts", icon_name="applications-graphics-symbolic")

        self.main_stack = Gtk.Stack()
        self.main_stack.add_named(scrolled_window, "list")
        self.main_stack.add_named(self.status_page, "status")
        main_box.append(self.main_stack)

        # UI Canvas
        self.canvas = Gtk.DrawingArea()
        self.canvas.set_hexpand(True)
        self.canvas.set_vexpand(True)
        self.canvas.set_draw_func(self.on_canvas_draw, None)
        main_box.append(self.canvas)

        # Properties Editor
        self.properties_editor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.properties_editor.set_size_request(200, -1)
        main_box.append(self.properties_editor)

        self.selection.connect("selection-changed", self._on_layout_selected)
        self._on_layout_selected(self.selection, None)

        click_gesture = Gtk.GestureClick.new()
        click_gesture.connect("pressed", self._on_canvas_click)
        self.canvas.add_controller(click_gesture)

        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        add_layout_button = Gtk.Button(label="Add Layout")
        add_layout_button.connect("clicked", self._on_add_layout)
        button_box.append(add_layout_button)

        delete_layout_button = Gtk.Button(label="Delete Layout")
        delete_layout_button.connect("clicked", self._on_delete_layout)
        button_box.append(delete_layout_button)

        add_element_button = Gtk.Button(label="Add Element")
        add_element_button.connect("clicked", self._on_add_element)
        button_box.append(add_element_button)

        delete_element_button = Gtk.Button(label="Delete Element")
        delete_element_button.connect("clicked", self._on_delete_element)
        button_box.append(delete_element_button)
        main_box.append(button_box)

        self._update_visibility()

    def _update_visibility(self):
        has_layouts = self.model.get_n_items() > 0
        print(f"DEBUG: UIBuilder._update_visibility: has_layouts={has_layouts}")
        if has_layouts:
            self.main_stack.set_visible_child_name("list")
        else:
            self.main_stack.set_visible_child_name("status")

    def _on_canvas_click(self, gesture, n_press, x, y):
        print(f"DEBUG: UIBuilder._on_canvas_click at ({x}, {y})")
        if not self.active_layout:
            return

        element_clicked = None
        for element in self.active_layout.layout.elements:
            if x >= element.x and x <= element.x + element.width and y >= element.y and y <= element.y + element.height:
                element_clicked = element
                break

        self.active_element = element_clicked
        self._populate_properties_editor(self.active_element)

    def _create_column(self, title, expression_func):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda _, list_item: list_item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda _, list_item: list_item.get_child().set_label(expression_func(list_item.get_item())))

        col = Gtk.ColumnViewColumn(title=title, factory=factory)
        self.layout_list.append_column(col)

    def _on_layout_selected(self, selection, _):
        print("DEBUG: UIBuilder._on_layout_selected")
        selected_layout = selection.get_selected_item()
        if selected_layout:
            self.active_layout = selected_layout
            self.canvas.queue_draw()
        else:
            self.active_layout = None
            self.canvas.queue_draw()
        self._clear_properties_editor()

    def on_canvas_draw(self, drawing_area, cr, width, height, data):
        cr.set_source_rgb(0.15, 0.15, 0.15)
        cr.paint()
        if self.active_layout:
            for element in self.active_layout.layout.elements:
                self._draw_element(cr, element)

    def _draw_element(self, cr, element):
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.rectangle(element.x, element.y, element.width, element.height)
        cr.fill()
        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.move_to(element.x + 5, element.y + 15)
        cr.show_text(f"{element.type}: {element.id}")

    def _on_add_layout(self, button):
        print("DEBUG: UIBuilder._on_add_layout")
        new_layout = UILayout(id=f"layout_{self.model.get_n_items() + 1}", name="New Layout")
        self.project_manager.add_ui_layout(new_layout)
        self.model.append(UILayoutGObject(new_layout))
        self._update_visibility()

    def _on_delete_layout(self, button):
        print("DEBUG: UIBuilder._on_delete_layout")
        selected_layout = self.selection.get_selected_item()
        if selected_layout:
            self.project_manager.remove_ui_layout(selected_layout.id)
            for i, item in enumerate(self.model):
                if item.id == selected_layout.id:
                    self.model.remove(i)
                    break
            self._update_visibility()

    def _on_add_element(self, button):
        print("DEBUG: UIBuilder._on_add_element")
        if self.active_layout:
            new_element = self.project_manager.add_element_to_layout(self.active_layout.id, f"elem_{len(self.active_layout.layout.elements) + 1}", "Button", 10, 10, 100, 30)
            self.canvas.queue_draw()

    def _on_delete_element(self, button):
        print("DEBUG: UIBuilder._on_delete_element")
        if self.active_layout and self.active_element:
            self.project_manager.remove_element_from_layout(self.active_layout.id, self.active_element.id)
            self.active_element = None
            self.canvas.queue_draw()
            self._clear_properties_editor()

    def _clear_properties_editor(self):
        print("DEBUG: UIBuilder._clear_properties_editor")
        while child := self.properties_editor.get_first_child():
            self.properties_editor.remove(child)

    def _populate_properties_editor(self, element):
        self._clear_properties_editor()
        if not element:
            return

        print(f"DEBUG: UIBuilder._populate_properties_editor for element: {element.id}")
        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        self.properties_editor.append(grid)

        grid.attach(Gtk.Label(label="ID:"), 0, 0, 1, 1)
        id_entry = Gtk.Entry(text=element.id)
        id_entry.connect("changed", self._on_element_detail_changed, element, "id")
        grid.attach(id_entry, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Type:"), 0, 1, 1, 1)
        type_entry = Gtk.Entry(text=element.type)
        type_entry.connect("changed", self._on_element_detail_changed, element, "type")
        grid.attach(type_entry, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label="X:"), 0, 2, 1, 1)
        x_spin = Gtk.SpinButton(adjustment=Gtk.Adjustment(lower=0, upper=9999, step_increment=1), value=element.x)
        x_spin.connect("value-changed", self._on_element_detail_changed, element, "x")
        grid.attach(x_spin, 1, 2, 1, 1)

        grid.attach(Gtk.Label(label="Y:"), 0, 3, 1, 1)
        y_spin = Gtk.SpinButton(adjustment=Gtk.Adjustment(lower=0, upper=9999, step_increment=1), value=element.y)
        y_spin.connect("value-changed", self._on_element_detail_changed, element, "y")
        grid.attach(y_spin, 1, 3, 1, 1)

        grid.attach(Gtk.Label(label="Width:"), 0, 4, 1, 1)
        width_spin = Gtk.SpinButton(adjustment=Gtk.Adjustment(lower=0, upper=9999, step_increment=1), value=element.width)
        width_spin.connect("value-changed", self._on_element_detail_changed, element, "width")
        grid.attach(width_spin, 1, 4, 1, 1)

        grid.attach(Gtk.Label(label="Height:"), 0, 5, 1, 1)
        height_spin = Gtk.SpinButton(adjustment=Gtk.Adjustment(lower=0, upper=9999, step_increment=1), value=element.height)
        height_spin.connect("value-changed", self._on_element_detail_changed, element, "height")
        grid.attach(height_spin, 1, 5, 1, 1)

    def _on_element_detail_changed(self, widget, element, property_name):
        print(f"DEBUG: UIBuilder._on_element_detail_changed: {property_name}")
        if isinstance(widget, Gtk.Entry):
            new_value = widget.get_text()
        elif isinstance(widget, Gtk.SpinButton):
            new_value = widget.get_value_as_int()
        else:
            return

        setattr(element, property_name, new_value)
        self.project_manager.set_dirty(True)
        self.canvas.queue_draw()
