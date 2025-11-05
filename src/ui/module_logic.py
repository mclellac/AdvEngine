import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw, Gio, PangoCairo, Pango, GdkPixbuf, GLib
import json
import os
from ..core.data_schemas import LogicNode, DialogueNode, ConditionNode, ActionNode, LogicGraph
from ..core.ue_exporter import get_command_definitions

class MiniMap(Gtk.DrawingArea):
    def __init__(self, logic_editor_canvas):
        super().__init__()
        self.logic_editor_canvas = logic_editor_canvas
        self.set_draw_func(self.on_draw, None)
        self.set_size_request(200, 150)

    def on_draw(self, drawing_area, cr, width, height, data):
        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.paint()

        active_graph = self.logic_editor_canvas.active_graph
        if not active_graph or not active_graph.nodes:
            return

        min_x = min(node.x for node in active_graph.nodes)
        min_y = min(node.y for node in active_graph.nodes)
        max_x = max(node.x + node.width for node in active_graph.nodes)
        max_y = max(node.y + node.height for node in active_graph.nodes)

        graph_width = max_x - min_x
        graph_height = max_y - min_y

        if graph_width == 0 or graph_height == 0: return

        scale = min(width / graph_width, height / graph_height) * 0.9
        offset_x = (width - (graph_width * scale)) / 2 - (min_x * scale)
        offset_y = (height - (graph_height * scale)) / 2 - (min_y * scale)

        for node in active_graph.nodes:
            cr.set_source_rgb(0.5, 0.5, 0.5)
            cr.rectangle(node.x * scale + offset_x, node.y * scale + offset_y, node.width * scale, node.height * scale)
            cr.fill()

class DynamicNodeEditor(Adw.Bin):
    def __init__(self, project_manager=None, on_update_callback=None):
        super().__init__()
        self.node = None
        self.project_manager = project_manager
        self.on_update_callback = on_update_callback
        self.main_widgets = {}
        self.param_widgets = {}

        self.container_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(self.container_box)

        self.main_group = None
        self.params_group = None

    def set_node(self, node):
        self.node = node
        GLib.idle_add(self.build_ui)

    def build_ui(self):
        if self.main_group:
            self.container_box.remove(self.main_group)
        if self.params_group:
            self.container_box.remove(self.params_group)

        self.main_widgets.clear()
        self.param_widgets.clear()

        self.main_group = Adw.PreferencesGroup()
        self.params_group = Adw.PreferencesGroup()
        self.container_box.append(self.main_group)
        self.container_box.append(self.params_group)

        if not self.node:
            self.params_group.set_visible(False)
            self.main_group.set_visible(False)
            return

        self.main_group.set_visible(True)

        if isinstance(self.node, DialogueNode):
            self.add_entry(self.main_group, "character_id", "Character ID", self.node.character_id)
            self.add_entry(self.main_group, "dialogue_text", "Dialogue Text", self.node.dialogue_text)
        elif isinstance(self.node, (ConditionNode, ActionNode)):
            defs = get_command_definitions()
            command_key = "conditions" if isinstance(self.node, ConditionNode) else "actions"
            command_type_key = "condition_type" if isinstance(self.node, ConditionNode) else "action_command"
            command_types = list(defs[command_key].keys())
            self.add_dropdown(self.main_group, command_type_key, "Type", command_types, getattr(self.node, command_type_key))
            self.update_params_ui()

    def add_entry(self, group, key, title, default_value):
        entry = Adw.EntryRow(title=title)
        entry.set_text(str(default_value))
        entry.connect("apply", self.on_value_changed)
        self.main_widgets[key] = entry
        group.add(entry)

    def add_dropdown(self, group, key, title, options, default_value):
        combo = Adw.ComboRow(title=title, model=Gtk.StringList.new(options))
        if default_value in options:
            combo.set_selected(options.index(default_value))
        combo.connect("notify::selected-item", self.on_combo_changed)
        self.main_widgets[key] = combo
        group.add(combo)

    def update_params_ui(self, *args):
        if self.params_group:
            self.container_box.remove(self.params_group)
        self.param_widgets.clear()

        self.params_group = Adw.PreferencesGroup()
        self.container_box.append(self.params_group)

        if not isinstance(self.node, (ConditionNode, ActionNode)):
            self.params_group.set_visible(False)
            return

        self.params_group.set_visible(True)
        command_key = "conditions" if isinstance(self.node, ConditionNode) else "actions"
        command_type_key = "condition_type" if isinstance(self.node, ConditionNode) else "action_command"
        selected_command = self.main_widgets[command_type_key].get_selected_item().get_string()

        if selected_command:
            defs = get_command_definitions()[command_key][selected_command]
            self.params_group.set_title(f"Parameters for {selected_command}")
            for param, p_type in defs["params"].items():
                self.add_param_widget(param, p_type, getattr(self.node, param.lower(), ""))

    def add_param_widget(self, key, param_type, default_value):
        # Convert snake_case to Title Case for display
        title = key.replace("_", " ").title()
        if isinstance(param_type, list):
            combo = Adw.ComboRow(title=title, model=Gtk.StringList.new(param_type))
            if default_value in param_type:
                combo.set_selected(param_type.index(default_value))
            combo.connect("notify::selected-item", self.on_value_changed)
            self.param_widgets[key.lower()] = combo
            self.params_group.add(combo)
        else:
            entry = Adw.EntryRow(title=title)
            entry.set_text(str(default_value))
            entry.connect("apply", self.on_value_changed)
            self.param_widgets[key.lower()] = entry
            self.params_group.add(entry)

    def on_combo_changed(self, combo, _):
        self.on_value_changed(combo)
        self.update_params_ui()

    def on_value_changed(self, widget):
        if not self.node: return
        values = self.get_values()
        for key, value in values.items():
            # Handle type conversion for int/bool
            field_type = type(getattr(self.node, key, None))
            if field_type == int:
                try: value = int(value)
                except (ValueError, TypeError): value = 0
            elif field_type == bool:
                value = str(value).lower() in ['true', '1']
            setattr(self.node, key, value)

        if self.project_manager:
            self.project_manager.set_dirty(True)
        if self.on_update_callback:
            self.on_update_callback()

    def get_values(self):
        values = {}
        all_widgets = {**self.main_widgets, **self.param_widgets}
        for key, widget in all_widgets.items():
            if isinstance(widget, Adw.EntryRow):
                values[key] = widget.get_text()
            elif isinstance(widget, Adw.ComboRow):
                selected_item = widget.get_selected_item()
                if selected_item:
                    values[key] = selected_item.get_string()
        return values

class LogicEditor(Gtk.Box):
    EDITOR_NAME = "Logic"
    VIEW_NAME = "logic_editor"
    ORDER = 1

    def __init__(self, project_manager):
        super().__init__()
        self.project_manager = project_manager
        self.active_graph = None
        self.selected_nodes = []
        self.connecting_from_node = None
        self.resizing_node = None
        self.drag_selection_rect = None

        self.drag_offsets = {}
        self.initial_node_width = 0
        self.initial_node_height = 0

        self.split_view = Adw.OverlaySplitView()
        self.append(self.split_view)

        self.split_view.set_sidebar_position(Gtk.PackType.START)
        self.split_view.set_content(self._create_canvas_area())
        self.split_view.set_sidebar(self._create_sidebar())

        if self.project_manager.data.logic_graphs:
            self.active_graph = self.project_manager.data.logic_graphs[0]
        else:
            self.active_graph = LogicGraph(id="default_graph", name="Default")
            self.project_manager.data.logic_graphs.append(self.active_graph)

        self.canvas.queue_draw()

        node_drag = Gtk.GestureDrag.new()
        node_drag.connect("drag-begin", self.on_drag_begin)
        node_drag.connect("drag-update", self.on_drag_update)
        node_drag.connect("drag-end", self.on_drag_end)
        self.canvas.add_controller(node_drag)

        click_gesture = Gtk.GestureClick.new()
        click_gesture.connect("pressed", self.on_canvas_click)
        self.canvas.add_controller(click_gesture)

        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.canvas.add_controller(key_controller)

        connection_drag = Gtk.GestureDrag.new()
        connection_drag.connect("drag-begin", self.on_connection_drag_begin)
        connection_drag.connect("drag-update", self.on_connection_drag_update)
        connection_drag.connect("drag-end", self.on_connection_drag_end)
        self.canvas.add_controller(connection_drag)

        resize_drag = Gtk.GestureDrag.new()
        resize_drag.connect("drag-begin", self.on_resize_drag_begin)
        resize_drag.connect("drag-update", self.on_resize_drag_update)
        resize_drag.connect("drag-end", self.on_resize_drag_end)
        self.canvas.add_controller(resize_drag)

        right_click_gesture = Gtk.GestureClick.new()
        right_click_gesture.set_button(Gdk.BUTTON_SECONDARY)
        right_click_gesture.connect("pressed", self.on_right_click)
        self.canvas.add_controller(right_click_gesture)

        self.create_canvas_context_menu()
        self.create_node_context_menu()

    def _create_canvas_area(self):
        canvas_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.canvas = Gtk.DrawingArea(hexpand=True, vexpand=True)
        self.canvas.set_draw_func(self.on_canvas_draw, None)
        canvas_container.append(self.canvas)
        self.minimap = MiniMap(self)
        canvas_container.append(self.minimap)
        return canvas_container

    def _create_sidebar(self):
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        sidebar.set_margin_top(12)
        sidebar.set_margin_bottom(12)
        sidebar.set_margin_start(12)
        sidebar.set_margin_end(12)

        palette = Adw.PreferencesGroup(title="Tool Palette")
        sidebar.append(palette)

        self.add_node_button(palette, "Add Dialogue Node", "Add Dialogue", DialogueNode, "Dialogue")
        self.add_node_button(palette, "Add Condition Node", "Add Condition", ConditionNode, "Condition")
        self.add_node_button(palette, "Add Action Node", "Add Action", ActionNode, "Action")

        self.props_panel = DynamicNodeEditor(project_manager=self.project_manager, on_update_callback=self.canvas.queue_draw)
        sidebar.append(self.props_panel)

        return sidebar

    def on_canvas_draw(self, area, cr, w, h, _):
        cr.set_source_rgb(0.15, 0.15, 0.15)
        cr.paint()
        if self.active_graph:
            for node in self.active_graph.nodes:
                self.draw_node(cr, node)
                for output_node_id in node.outputs:
                    output_node = next((n for n in self.active_graph.nodes if n.id == output_node_id), None)
                    if output_node:
                        self.draw_connection(cr, node, output_node)
            if self.connecting_from_node:
                start_x, start_y = self.get_connector_pos(self.connecting_from_node, "out")
                cr.set_source_rgb(0.8, 0.8, 0.2)
                cr.move_to(start_x, start_y)
                cr.line_to(self.connecting_line_x, self.connecting_line_y)
                cr.stroke()
            if self.drag_selection_rect:
                cr.set_source_rgba(0.2, 0.5, 1.0, 0.3)
                x1, y1, x2, y2 = self.drag_selection_rect
                cr.rectangle(min(x1,x2), min(y1,y2), abs(x1-x2), abs(y1-y2))
                cr.fill()

    def draw_node(self, cr, node):
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.rectangle(node.x, node.y, node.width, node.height)
        cr.fill()

        if isinstance(node, DialogueNode): cr.set_source_rgb(0.4, 0.6, 0.4)
        elif isinstance(node, ConditionNode): cr.set_source_rgb(0.6, 0.4, 0.4)
        elif isinstance(node, ActionNode): cr.set_source_rgb(0.4, 0.4, 0.6)
        else: cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.rectangle(node.x, node.y, node.width, 25)
        cr.fill()

        if node in self.selected_nodes:
            cr.set_source_rgb(1.0, 1.0, 0.0)
            cr.set_line_width(3)
            cr.rectangle(node.x - 2, node.y - 2, node.width + 4, node.height + 4)
            cr.stroke()

        layout = PangoCairo.create_layout(cr)
        layout.set_width((node.width - 20) * Pango.SCALE)
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)
        cr.set_source_rgb(1, 1, 1)
        layout.set_markup(f"<b>{node.node_type}</b>: {node.id}", -1)
        cr.move_to(node.x + 10, node.y + 5)
        PangoCairo.show_layout(cr, layout)

        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.move_to(node.x + 10, node.y + 35)
        body_text = ""
        if isinstance(node, DialogueNode): body_text = f"<b>Char:</b> {node.character_id}\n<i>\"{node.dialogue_text}\"</i>"
        elif isinstance(node, ConditionNode): body_text = f"<b>If:</b> {node.condition_type}"
        elif isinstance(node, ActionNode): body_text = f"<b>Do:</b> {node.action_command}"
        layout.set_markup(body_text, -1)
        PangoCairo.show_layout(cr, layout)

        self.draw_connectors_and_resize_handle(cr, node)

    def draw_connectors_and_resize_handle(self, cr, node):
        connector_y = node.y + node.height / 2
        cr.set_source_rgb(0.8, 0.8, 0.2)
        cr.rectangle(node.x - 5, connector_y - 5, 10, 10)
        cr.rectangle(node.x + node.width - 5, connector_y - 5, 10, 10)
        cr.fill()
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.rectangle(node.x + node.width - 10, node.y + node.height - 10, 10, 10)
        cr.fill()

    def draw_connection(self, cr, from_node, to_node):
        start_x, start_y = self.get_connector_pos(from_node, "out")
        end_x, end_y = self.get_connector_pos(to_node, "in")
        cr.set_source_rgb(0.8, 0.8, 0.2)
        cr.move_to(start_x, start_y)
        cr.curve_to(start_x + 50, start_y, end_x - 50, end_y, end_x, end_y)
        cr.stroke()

    def add_node_button(self, palette, title, label, node_class, node_type):
        button = Gtk.Button(label=label)
        button.connect("clicked", lambda w: self.on_add_node(node_class, node_type))
        row = Adw.ActionRow(title=title, activatable_widget=button)
        row.add_suffix(button)
        palette.add(row)

    def on_add_node(self, node_class, node_type):
        if self.active_graph:
            new_node = node_class(id=f"node_{len(self.active_graph.nodes)}", node_type=node_type, x=50, y=50)
            self.active_graph.nodes.append(new_node)
            self.canvas.queue_draw()
            self.minimap.queue_draw()
            self.project_manager.set_dirty(True)

    def get_connector_pos(self, node, connector_type):
        if connector_type == "in":
            return node.x, node.y + node.height / 2
        else:
            return node.x + node.width, node.y + node.height / 2

    def on_drag_begin(self, gesture, x, y):
        node_clicked = self.get_node_at(x, y)
        if node_clicked:
            if node_clicked not in self.selected_nodes:
                self.selected_nodes = [node_clicked]
                self.props_panel.set_node(node_clicked)
            self.drag_offsets = {n.id: (x - n.x, y - n.y) for n in self.selected_nodes}
            gesture.set_state(Gtk.EventSequenceState.CLAIMED)
        else:
            self.drag_selection_rect = [x, y, x, y]

    def on_drag_update(self, gesture, x, y):
        if self.drag_offsets:
            success, start_x, start_y = gesture.get_start_point()
            for node in self.selected_nodes:
                offset_x, offset_y = self.drag_offsets[node.id]
                node.x = start_x + x - offset_x
                node.y = start_y + y - offset_y
            self.canvas.queue_draw()
        elif self.drag_selection_rect:
            self.drag_selection_rect[2] = x
            self.drag_selection_rect[3] = y
            self.canvas.queue_draw()

    def on_drag_end(self, gesture, x, y):
        if self.drag_offsets:
            self.project_manager.set_dirty()
            self.drag_offsets = {}
        elif self.drag_selection_rect:
            self.selected_nodes.clear()
            x1, y1, x2, y2 = self.drag_selection_rect
            rect = Gdk.Rectangle()
            rect.x = min(x1, x2)
            rect.y = min(y1, y2)
            rect.width = abs(x1 - x2)
            rect.height = abs(y1 - y2)
            for node in self.active_graph.nodes:
                node_rect = Gdk.Rectangle()
                node_rect.x, node_rect.y, node_rect.width, node_rect.height = node.x, node.y, node.width, node.height
                if rect.intersect(node_rect)[0]:
                    self.selected_nodes.append(node)
            self.drag_selection_rect = None
            self.canvas.queue_draw()

    def on_canvas_click(self, gesture, n_press, x, y):
        node = self.get_node_at(x, y)
        if node:
            if not gesture.get_current_event_state() & Gdk.ModifierType.SHIFT_MASK:
                self.selected_nodes = [node]
            else:
                if node in self.selected_nodes: self.selected_nodes.remove(node)
                else: self.selected_nodes.append(node)
        else:
            self.selected_nodes = []
        self.props_panel.set_node(self.selected_nodes[0] if len(self.selected_nodes) == 1 else None)
        self.canvas.queue_draw()

    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Delete:
            for node_to_delete in self.selected_nodes:
                self.active_graph.nodes.remove(node_to_delete)
                for node in self.active_graph.nodes:
                    if node_to_delete.id in node.outputs: node.outputs.remove(node_to_delete.id)
                    if node_to_delete.id in node.inputs: node.inputs.remove(node_to_delete.id)
            self.selected_nodes.clear()
            self.props_panel.set_node(None)
            self.canvas.queue_draw()
            self.project_manager.set_dirty(True)

    def on_connection_drag_begin(self, gesture, x, y):
        for node in reversed(self.active_graph.nodes):
            out_x, out_y = self.get_connector_pos(node, "out")
            if abs(x - out_x) < 10 and abs(y - out_y) < 10:
                self.connecting_from_node = node
                self.connecting_line_x, self.connecting_line_y = x, y
                gesture.set_state(Gtk.EventSequenceState.CLAIMED)
                return

    def on_connection_drag_update(self, gesture, x, y):
        if self.connecting_from_node:
            success, start_x, start_y = gesture.get_start_point()
            self.connecting_line_x = start_x + x
            self.connecting_line_y = start_y + y
            self.canvas.queue_draw()

    def on_connection_drag_end(self, gesture, x, y):
        if self.connecting_from_node:
            for node in self.active_graph.nodes:
                in_x, in_y = self.get_connector_pos(node, "in")
                if abs(self.connecting_line_x - in_x) < 10 and abs(self.connecting_line_y - in_y) < 10 and node != self.connecting_from_node:
                    self.connecting_from_node.outputs.append(node.id)
                    node.inputs.append(self.connecting_from_node.id)
                    self.project_manager.set_dirty(True)
                    break
        self.connecting_from_node = None
        self.canvas.queue_draw()

    def on_resize_drag_begin(self, gesture, x, y):
        for node in reversed(self.active_graph.nodes):
            if x >= node.x + node.width - 10 and x <= node.x + node.width and \
               y >= node.y + node.height - 10 and y <= node.y + node.height:
                self.resizing_node = node
                self.initial_node_width = node.width
                self.initial_node_height = node.height
                gesture.set_state(Gtk.EventSequenceState.CLAIMED)
                return

    def on_resize_drag_update(self, gesture, x, y):
        if self.resizing_node:
            # The x and y values from the gesture are offsets from the start point
            self.resizing_node.width = max(150, self.initial_node_width + x)
            self.resizing_node.height = max(100, self.initial_node_height + y)
            self.canvas.queue_draw()

    def on_resize_drag_end(self, gesture, x, y):
        if self.resizing_node:
            self.project_manager.set_dirty(True)
            self.resizing_node = None

    def get_node_at(self, x, y):
        if self.active_graph:
            for node in reversed(self.active_graph.nodes):
                if x >= node.x and x <= node.x + node.width and y >= node.y and y <= node.y + node.height:
                    return node
        return None

    def on_right_click(self, gesture, n_press, x, y):
        node = self.get_node_at(x, y)
        if node:
            self.selected_nodes = [node]
            self.node_context_menu.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
            self.node_context_menu.popup()
        else:
            self.canvas_context_menu.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
            self.canvas_context_menu.popup()

    def create_canvas_context_menu(self):
        menu = Gio.Menu.new()
        menu.append("Add Dialogue Node", "app.add_dialogue_node")
        menu.append("Add Condition Node", "app.add_condition_node")
        menu.append("Add Action Node", "app.add_action_node")
        self.canvas_context_menu = Gtk.PopoverMenu.new_from_model(menu)
        self.canvas_context_menu.set_parent(self.canvas)

    def create_node_context_menu(self):
        menu = Gio.Menu.new()
        menu.append("Delete Node", "app.delete_node")
        self.node_context_menu = Gtk.PopoverMenu.new_from_model(menu)
        self.node_context_menu.set_parent(self.canvas)
