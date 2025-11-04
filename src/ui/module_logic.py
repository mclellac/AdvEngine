import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw, Gio, PangoCairo, Pango, GdkPixbuf
import json
import os
from ..core.data_schemas import LogicNode, DialogueNode, ConditionNode, ActionNode, LogicGraph
from ..core.ue_exporter import get_command_definitions

# Constants
MINI_MAP_WIDTH = 200
MINI_MAP_HEIGHT = 150
NODE_HEADER_HEIGHT = 25
CONNECTOR_SIZE = 10
RESIZE_HANDLE_SIZE = 10
NODE_MIN_WIDTH = 150
NODE_MIN_HEIGHT = 100

# Colors
COLOR_BACKGROUND = (0.15, 0.15, 0.15)
COLOR_NODE_BODY = (0.2, 0.2, 0.2)
COLOR_NODE_HEADER_DIALOGUE = (0.4, 0.6, 0.4)
COLOR_NODE_HEADER_CONDITION = (0.6, 0.4, 0.4)
COLOR_NODE_HEADER_ACTION = (0.4, 0.4, 0.6)
COLOR_NODE_HEADER_DEFAULT = (0.5, 0.5, 0.5)
COLOR_NODE_SELECTED_BORDER = (1.0, 1.0, 0.0)
COLOR_NODE_TEXT = (1.0, 1.0, 1.0)
COLOR_NODE_TEXT_SECONDARY = (0.9, 0.9, 0.9)
COLOR_CONNECTOR = (0.8, 0.8, 0.2)
COLOR_CONNECTION_LINE = (0.8, 0.8, 0.2)
COLOR_RESIZE_HANDLE = (0.5, 0.5, 0.5)
COLOR_SELECTION_RECT = (0.2, 0.5, 1.0, 0.3)

class MiniMap(Gtk.DrawingArea):
    def __init__(self, logic_editor_canvas):
        super().__init__()
        self.logic_editor_canvas = logic_editor_canvas
        self.set_draw_func(self.on_draw, None)
        self.set_size_request(MINI_MAP_WIDTH, MINI_MAP_HEIGHT)

    def on_draw(self, drawing_area, cr, width, height, data):
        cr.set_source_rgb(*COLOR_BACKGROUND)
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

class DynamicNodeEditor(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.node = None
        self.widgets = {}
        self.params_group = Adw.PreferencesGroup()
        self.main_group = Adw.PreferencesGroup()
        self.append(self.main_group)
        self.append(self.params_group)

    def set_node(self, node):
        self.node = node
        self.build_ui()

    def build_ui(self):
        # Clear existing widgets
        while self.main_group.get_first_child():
            self.main_group.remove(self.main_group.get_first_child())
        while self.params_group.get_first_child():
            self.params_group.remove(self.params_group.get_first_child())
        self.widgets.clear()

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
        self.widgets[key] = entry
        group.add(entry)

    def add_dropdown(self, group, key, title, options, default_value):
        combo = Adw.ComboRow(title=title, model=Gtk.StringList.new(options))
        self.widgets[key] = combo
        if default_value in options:
            combo.set_selected(options.index(default_value))
        combo.connect("notify::selected-item", self.on_combo_changed)
        group.add(combo)

    def update_params_ui(self, *args):
        # Clear existing parameter widgets safely
        while child := self.params_group.get_first_child():
            self.params_group.remove(child)

        if not isinstance(self.node, (ConditionNode, ActionNode)):
            self.params_group.set_visible(False)
            return

        self.params_group.set_visible(True)
        command_key = "conditions" if isinstance(self.node, ConditionNode) else "actions"
        command_type_key = "condition_type" if isinstance(self.node, ConditionNode) else "action_command"
        selected_command = self.widgets[command_type_key].get_selected_item().get_string()

        if selected_command:
            defs = get_command_definitions()[command_key][selected_command]
            self.params_group.set_title(f"Parameters")
            for param, p_type in defs["params"].items():
                default = self.node.parameters.get(param, "")
                self.add_param_widget(param, p_type, default)

    def add_param_widget(self, key, param_type, default_value):
        if isinstance(param_type, list):
            self.add_dropdown(self.params_group, key, key, param_type, default_value)
        else:
            self.add_entry(self.params_group, key, key, default_value)

    def on_combo_changed(self, combo, _):
        self.update_params_ui()
        self.on_value_changed(combo)

    def on_value_changed(self, widget):
        if not self.node: return
        values = self.get_values()
        for key, value in values.items():
            setattr(self.node, key, value)
        self.node.get_parent_editor().project_manager.set_dirty(True)
        self.node.get_parent_editor().canvas.queue_draw()

    def get_values(self):
        values = {}
        # Handle DialogueNode and other simple nodes
        if not isinstance(self.node, (ConditionNode, ActionNode)):
            for key, widget in self.widgets.items():
                if isinstance(widget, Adw.EntryRow):
                    values[key] = widget.get_text()
            return values

        # Handle ConditionNode and ActionNode
        command_type_key = "condition_type" if isinstance(self.node, ConditionNode) else "action_command"
        command_key = "conditions" if isinstance(self.node, ConditionNode) else "actions"

        command_type_widget = self.widgets[command_type_key]
        selected_command = command_type_widget.get_selected_item().get_string()
        values[command_type_key] = selected_command

        values['parameters'] = {}
        if not selected_command:
            return values

        try:
            param_defs = get_command_definitions()[command_key][selected_command]["params"]
        except KeyError:
            return values  # Command might not have params

        for param in param_defs.keys():
            widget = self.widgets.get(param)
            if isinstance(widget, Adw.ComboRow):
                values['parameters'][param] = widget.get_selected_item().get_string()
            elif isinstance(widget, Adw.EntryRow):
                values['parameters'][param] = widget.get_text()

        return values

class LogicEditor(Gtk.Box):
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

        # Connect signals
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

        # --- Tool Palette ---
        palette = Adw.PreferencesGroup(title="Tool Palette")
        sidebar.append(palette)

        dialogue_button = Gtk.Button(label="Add Dialogue")
        dialogue_button.connect("clicked", lambda _: self.on_add_node(DialogueNode, "Dialogue"))
        dialogue_row = Adw.ActionRow(title="Add Dialogue Node", activatable_widget=dialogue_button)
        dialogue_row.add_suffix(dialogue_button)
        palette.add(dialogue_row)

        condition_button = Gtk.Button(label="Add Condition")
        condition_button.connect("clicked", lambda _: self.on_add_node(ConditionNode, "Condition"))
        condition_row = Adw.ActionRow(title="Add Condition Node", activatable_widget=condition_button)
        condition_row.add_suffix(condition_button)
        palette.add(condition_row)

        action_button = Gtk.Button(label="Add Action")
        action_button.connect("clicked", lambda _: self.on_add_node(ActionNode, "Action"))
        action_row = Adw.ActionRow(title="Add Action Node", activatable_widget=action_button)
        action_row.add_suffix(action_button)
        palette.add(action_row)

        # --- Properties Panel ---
        self.props_panel = DynamicNodeEditor()
        sidebar.append(self.props_panel)

        return sidebar

    def on_canvas_draw(self, area, cr, w, h, _):
        cr.set_source_rgb(*COLOR_BACKGROUND)
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
                cr.set_source_rgb(*COLOR_CONNECTION_LINE)
                cr.move_to(start_x, start_y)
                cr.line_to(self.connecting_line_x, self.connecting_line_y)
                cr.stroke()
            if self.drag_selection_rect:
                cr.set_source_rgba(*COLOR_SELECTION_RECT)
                x1, y1, x2, y2 = self.drag_selection_rect
                cr.rectangle(min(x1,x2), min(y1,y2), abs(x1-x2), abs(y1-y2))
                cr.fill()

    def draw_node(self, cr, node):
        # Node body
        cr.set_source_rgb(*COLOR_NODE_BODY)
        cr.rectangle(node.x, node.y, node.width, node.height)
        cr.fill()

        # Node Header
        if isinstance(node, DialogueNode): cr.set_source_rgb(*COLOR_NODE_HEADER_DIALOGUE)
        elif isinstance(node, ConditionNode): cr.set_source_rgb(*COLOR_NODE_HEADER_CONDITION)
        elif isinstance(node, ActionNode): cr.set_source_rgb(*COLOR_NODE_HEADER_ACTION)
        else: cr.set_source_rgb(*COLOR_NODE_HEADER_DEFAULT)
        cr.rectangle(node.x, node.y, node.width, NODE_HEADER_HEIGHT)
        cr.fill()

        if node in self.selected_nodes:
            cr.set_source_rgb(*COLOR_NODE_SELECTED_BORDER)
            cr.set_line_width(3)
            cr.rectangle(node.x - 2, node.y - 2, node.width + 4, node.height + 4)
            cr.stroke()

        # Node text
        layout = PangoCairo.create_layout(cr)
        layout.set_width((node.width - 20) * Pango.SCALE)
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)
        cr.set_source_rgb(*COLOR_NODE_TEXT)
        layout.set_markup(f"<b>{node.node_type}</b>: {node.id}", -1)
        cr.move_to(node.x + 10, node.y + 5)
        PangoCairo.show_layout(cr, layout)

        cr.set_source_rgb(*COLOR_NODE_TEXT_SECONDARY)
        cr.move_to(node.x + 10, node.y + 35)
        body_text = ""
        if isinstance(node, DialogueNode): body_text = f"<b>Char:</b> {node.character_id}\n<i>\"{node.dialogue_text}\"</i>"
        elif isinstance(node, ConditionNode): body_text = f"<b>If:</b> {node.condition_type}"
        elif isinstance(node, ActionNode): body_text = f"<b>Do:</b> {node.action_command}"
        layout.set_markup(body_text, -1)
        PangoCairo.show_layout(cr, layout)

        # Connectors & Resize handle
        self.draw_connectors_and_resize_handle(cr, node)

    def draw_connectors_and_resize_handle(self, cr, node):
        connector_y = node.y + node.height / 2
        cr.set_source_rgb(*COLOR_CONNECTOR)
        cr.rectangle(node.x - CONNECTOR_SIZE / 2, connector_y - CONNECTOR_SIZE / 2, CONNECTOR_SIZE, CONNECTOR_SIZE)
        cr.rectangle(node.x + node.width - CONNECTOR_SIZE / 2, connector_y - CONNECTOR_SIZE / 2, CONNECTOR_SIZE, CONNECTOR_SIZE)
        cr.fill()
        cr.set_source_rgb(*COLOR_RESIZE_HANDLE)
        cr.rectangle(node.x + node.width - RESIZE_HANDLE_SIZE, node.y + node.height - RESIZE_HANDLE_SIZE, RESIZE_HANDLE_SIZE, RESIZE_HANDLE_SIZE)
        cr.fill()

    def draw_connection(self, cr, from_node, to_node):
        start_x, start_y = self.get_connector_pos(from_node, "out")
        end_x, end_y = self.get_connector_pos(to_node, "in")
        cr.set_source_rgb(*COLOR_CONNECTION_LINE)
        cr.move_to(start_x, start_y)
        cr.curve_to(start_x + 50, start_y, end_x - 50, end_y, end_x, end_y)
        cr.stroke()

    def on_add_node(self, node_class, node_type):
        if self.active_graph:
            new_node = node_class(id=f"node_{len(self.active_graph.nodes)}", node_type=node_type, x=50, y=50, parent_editor=self)
            self.active_graph.nodes.append(new_node)
            self.canvas.queue_draw()
            self.minimap.queue_draw()
            self.project_manager.set_dirty(True)


    def get_connector_pos(self, node, connector_type):
        if connector_type == "in":
            return node.x, node.y + node.height / 2
        else: # out
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
            start_x, start_y = self.drag_selection_rect[:2]
            self.drag_selection_rect = [start_x, start_y, x, y]
            self.canvas.queue_draw()

    def on_drag_end(self, gesture, x, y):
        if self.drag_offsets:
            self.project_manager.set_dirty()
            self.drag_offsets = {}
        elif self.drag_selection_rect:
            # Finalize selection
            self.selected_nodes.clear()
            x1, y1, x2, y2 = self.drag_selection_rect
            rect = Gdk.Rectangle()
            rect.x = min(x1, x2)
            rect.y = min(y1, y2)
            rect.width = abs(x1 - x2)
            rect.height = abs(y1 - y2)

            for node in self.active_graph.nodes:
                node_rect = Gdk.Rectangle()
                node_rect.x = node.x
                node_rect.y = node.y
                node_rect.width = node.width
                node_rect.height = node.height
                if rect.intersect(node_rect)[0]:
                    self.selected_nodes.append(node)
            self.drag_selection_rect = None
            self.canvas.queue_draw()

    def on_canvas_click(self, gesture, n_press, x, y):
        node = self.get_node_at(x, y)
        if node:
            if n_press == 2:
                # Could be used for quick inline edit later
                pass
            else:
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
                # Remove connections
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
            if x >= node.x + node.width - RESIZE_HANDLE_SIZE and x <= node.x + node.width and \
               y >= node.y + node.height - RESIZE_HANDLE_SIZE and y <= node.y + node.height:
                self.resizing_node = node
                self.initial_node_width = node.width
                self.initial_node_height = node.height
                gesture.set_state(Gtk.EventSequenceState.CLAIMED)
                return

    def on_resize_drag_update(self, gesture, x, y):
        if self.resizing_node:
            success, start_x, start_y = gesture.get_start_point()
            self.resizing_node.width = max(NODE_MIN_WIDTH, self.initial_node_width + x)
            self.resizing_node.height = max(NODE_MIN_HEIGHT, self.initial_node_height + y)
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
        menu.append("Add Dialogue Node", "app.add-dialogue-node")
        menu.append("Add Condition Node", "app.add-condition-node")
        menu.append("Add Action Node", "app.add-action-node")
        self.canvas_context_menu = Gtk.PopoverMenu.new_from_model(menu)
        self.canvas_context_menu.set_parent(self.canvas)

    def create_node_context_menu(self):
        menu = Gio.Menu.new()
        menu.append("Delete Node", "app.delete_node")
        self.node_context_menu = Gtk.PopoverMenu.new_from_model(menu)
        self.node_context_menu.set_parent(self.canvas)

