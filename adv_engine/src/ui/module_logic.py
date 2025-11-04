import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw, Gio, PangoCairo, Pango, GdkPixbuf
import json
import os
from ..core.data_schemas import LogicNode, DialogueNode, ConditionNode, ActionNode, LogicGraph
from ..core.ue_exporter import get_command_definitions

class MiniMap(Gtk.DrawingArea):
    def __init__(self, logic_editor_canvas, active_graph):
        super().__init__()
        self.logic_editor_canvas = logic_editor_canvas
        self.active_graph = active_graph
        self.set_draw_func(self.on_draw, None)
        self.set_size_request(200, 150)

    def on_draw(self, drawing_area, cr, width, height, data):
        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.paint()

        if not self.active_graph or not self.active_graph.nodes:
            return

        # Calculate bounding box of all nodes
        min_x = min(node.x for node in self.active_graph.nodes)
        min_y = min(node.y for node in self.active_graph.nodes)
        max_x = max(node.x + 150 for node in self.active_graph.nodes)
        max_y = max(node.y + 80 for node in self.active_graph.nodes)

        graph_width = max_x - min_x
        graph_height = max_y - min_y

        if graph_width == 0 or graph_height == 0:
            return

        # Calculate scale factor
        scale_x = width / graph_width
        scale_y = height / graph_height
        scale = min(scale_x, scale_y) * 0.9  # 90% padding

        # Center the graph
        offset_x = (width - (graph_width * scale)) / 2 - (min_x * scale)
        offset_y = (height - (graph_height * scale)) / 2 - (min_y * scale)

        # Draw nodes
        for node in self.active_graph.nodes:
            cr.set_source_rgb(0.5, 0.5, 0.5)
            cr.rectangle(node.x * scale + offset_x, node.y * scale + offset_y, 150 * scale, 80 * scale)
            cr.fill()

class DynamicNodeEditor(Gtk.Box):
    def __init__(self, node):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.node = node
        self.widgets = {}
        self.build_ui()

    def build_ui(self):
        group = Adw.PreferencesGroup()
        self.append(group)

        if isinstance(self.node, DialogueNode):
            self.add_entry(group, "character_id", "Character ID", "The ID of the character speaking.", self.node.character_id)
            self.add_entry(group, "dialogue_text", "Dialogue Text", "The line of dialogue.", self.node.dialogue_text)
        elif isinstance(self.node, (ConditionNode, ActionNode)):
            defs = get_command_definitions()
            command_key = "conditions" if isinstance(self.node, ConditionNode) else "actions"
            command_type_key = "condition_type" if isinstance(self.node, ConditionNode) else "action_command"

            # Dropdown for command type
            command_types = list(defs[command_key].keys())
            self.add_dropdown(group, command_type_key, "Type", "The type of command.", command_types, getattr(self.node, command_type_key))

            # Parameters Box
            self.params_group = Adw.PreferencesGroup()
            self.append(self.params_group)
            self.update_params_ui(None) # Initial population

    def add_entry(self, group, key, title, subtitle, default_value):
        entry = Gtk.Entry(text=str(default_value))
        self.widgets[key] = entry
        row = self._create_action_row(title, subtitle, entry)
        group.add(row)

    def add_dropdown(self, group, key, title, subtitle, options, default_value):
        dropdown = Gtk.DropDown.new_from_strings(options)
        self.widgets[key] = dropdown
        if default_value in options:
            dropdown.set_selected(options.index(default_value))
        dropdown.connect("notify::selected-item", self.update_params_ui)
        row = self._create_action_row(title, subtitle, dropdown)
        group.add(row)

    def _create_action_row(self, title, subtitle, widget):
        row = Adw.ActionRow(title=title, subtitle=subtitle)
        row.add_suffix(widget)
        row.set_activatable_widget(widget)
        return row

    def update_params_ui(self, dropdown, _=None):
        # Clear existing params
        for child in list(self.params_group.observe_children()):
            self.params_group.remove(child)

        command_key = "conditions" if isinstance(self.node, ConditionNode) else "actions"
        command_type_key = "condition_type" if isinstance(self.node, ConditionNode) else "action_command"

        selected_command = self.widgets[command_type_key].get_selected_item().get_string()

        if selected_command:
            defs = get_command_definitions()[command_key][selected_command]
            self.params_group.set_title(f"{selected_command} Parameters")
            self.params_group.set_description(defs.get("description", ""))
            for param, p_type in defs["params"].items():
                default = self.node.parameters.get(param, "")
                self.add_param_widget(param, p_type, default)

    def add_param_widget(self, key, param_type, default_value):
        if isinstance(param_type, list): # It's a dropdown
            dropdown = Gtk.DropDown.new_from_strings(param_type)
            if default_value in param_type:
                dropdown.set_selected(param_type.index(default_value))
            self.widgets[key] = dropdown
            row = self._create_action_row(key, "", dropdown)
            self.params_group.add(row)
        else: # It's an entry
            entry = Gtk.Entry(text=str(default_value))
            self.widgets[key] = entry
            row = self._create_action_row(key, "", entry)
            self.params_group.add(row)

    def get_values(self):
        values = {}
        if isinstance(self.node, (ConditionNode, ActionNode)):
            command_type_key = "condition_type" if isinstance(self.node, ConditionNode) else "action_command"
            values[command_type_key] = self.widgets[command_type_key].get_selected_item().get_string()
            values['parameters'] = {}
            command_key = "conditions" if isinstance(self.node, ConditionNode) else "actions"
            selected_command = self.widgets[command_type_key].get_selected_item().get_string()
            if selected_command:
                defs = get_command_definitions()[command_key][selected_command]["params"]
                for param, p_type in defs.items():
                    if isinstance(p_type, list):
                        values['parameters'][param] = self.widgets[param].get_selected_item().get_string()
                    else:
                         values['parameters'][param] = self.widgets[param].get_text()
        else:
            for key, widget in self.widgets.items():
                values[key] = widget.get_text()
        return values

class LogicEditor(Gtk.Box):
    def on_delete_node(self, button):
        if self.selected_nodes and self.active_graph:
            for node_to_delete in self.selected_nodes:
                self.active_graph.nodes.remove(node_to_delete)
                # Remove any connections to the deleted node
                for node in self.active_graph.nodes:
                    if node_to_delete.id in node.outputs:
                        node.outputs.remove(node_to_delete.id)
                    if node_to_delete.id in node.inputs:
                        node.inputs.remove(node_to_delete.id)

            self.selected_nodes.clear()
            self.delete_node_button.set_sensitive(False)
            self.project_manager.set_dirty()
            self.canvas.queue_draw()
            self.minimap.queue_draw()

    def edit_node_dialog(self, node):
        dialog = Gtk.Dialog(title=f"Edit Node {node.id}", transient_for=self.get_native(), modal=True)
        dialog.add_buttons("_Cancel", Gtk.ResponseType.CANCEL, "_Save", Gtk.ResponseType.OK)

        editor = DynamicNodeEditor(node)
        dialog.get_content_area().append(editor)

        def on_response(dialog, response_id):
            if response_id == Gtk.ResponseType.OK:
                values = editor.get_values()
                for key, value in values.items():
                    setattr(node, key, value)
                self.project_manager.set_dirty()
                self.canvas.queue_draw()
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.show()

    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.project_manager = project_manager
        self.dragging_node = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.active_graph = None
        self.selected_nodes = []
        self.connecting_from_node = None
        self.connecting_line_x = 0
        self.connecting_line_y = 0
        self.resizing_node = None

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        if self.project_manager.data.logic_graphs:
            self.active_graph = self.project_manager.data.logic_graphs[0]
        else:
            self.active_graph = LogicGraph(id="default_graph", name="Default")
            self.project_manager.data.logic_graphs.append(self.active_graph)

        palette = Adw.PreferencesGroup()
        palette.set_size_request(200, -1)

        dialogue_row = Adw.ActionRow(title="Add Dialogue Node")
        dialogue_button = Gtk.Button(label="Add")
        dialogue_button.set_tooltip_text("Create a new dialogue node")
        dialogue_button.connect("clicked", self.on_add_dialogue_node)
        dialogue_row.add_suffix(dialogue_button)
        dialogue_row.set_activatable_widget(dialogue_button)
        palette.add(dialogue_row)

        condition_row = Adw.ActionRow(title="Add Condition Node")
        condition_button = Gtk.Button(label="Add")
        condition_button.set_tooltip_text("Create a new condition node")
        condition_button.connect("clicked", self.on_add_condition_node)
        condition_row.add_suffix(condition_button)
        condition_row.set_activatable_widget(condition_button)
        palette.add(condition_row)

        action_row = Adw.ActionRow(title="Add Action Node")
        action_button = Gtk.Button(label="Add")
        action_button.set_tooltip_text("Create a new action node")
        action_button.connect("clicked", self.on_add_action_node)
        action_row.add_suffix(action_button)
        action_row.set_activatable_widget(action_button)
        palette.add(action_row)

        self.delete_node_row = Adw.ActionRow(title="Delete Selected Node(s)")
        self.delete_node_button = Gtk.Button(label="Delete")
        self.delete_node_button.set_tooltip_text("Delete the selected node(s) (Del)")
        self.delete_node_button.set_sensitive(False)
        self.delete_node_button.connect("clicked", self.on_delete_node)
        self.delete_node_row.add_suffix(self.delete_node_button)
        self.delete_node_row.set_activatable_widget(self.delete_node_button)
        palette.add(self.delete_node_row)

        self.append(palette)

        canvas_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        canvas_container.set_hexpand(True)
        canvas_container.set_vexpand(True)

        self.canvas = Gtk.DrawingArea()
        self.canvas.set_hexpand(True)
        self.canvas.set_vexpand(True)
        self.canvas.set_draw_func(self.on_canvas_draw, None)
        self.canvas.set_focusable(True)
        canvas_container.append(self.canvas)

        self.minimap = MiniMap(self.canvas, self.active_graph)
        canvas_container.append(self.minimap)

        self.append(canvas_container)

        node_drag = Gtk.GestureDrag.new()
        node_drag.connect("drag-begin", self.on_drag_begin)
        node_drag.connect("drag-update", self.on_drag_update)
        node_drag.connect("drag-end", self.on_drag_end)
        self.canvas.add_controller(node_drag)

        connection_drag = Gtk.GestureDrag.new()
        connection_drag.connect("drag-begin", self.on_connection_drag_begin)
        connection_drag.connect("drag-update", self.on_connection_drag_update)
        connection_drag.connect("drag-end", self.on_connection_drag_end)
        self.canvas.add_controller(connection_drag)

        click_gesture = Gtk.GestureClick.new()
        click_gesture.connect("pressed", self.on_canvas_click)
        self.canvas.add_controller(click_gesture)

        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.canvas.add_controller(key_controller)

        right_click_gesture = Gtk.GestureClick.new()
        right_click_gesture.set_button(Gdk.BUTTON_SECONDARY)
        right_click_gesture.connect("pressed", self.on_right_click)
        self.canvas.add_controller(right_click_gesture)

        resize_drag = Gtk.GestureDrag.new()
        resize_drag.connect("drag-begin", self.on_resize_drag_begin)
        resize_drag.connect("drag-update", self.on_resize_drag_update)
        resize_drag.connect("drag-end", self.on_resize_drag_end)
        self.canvas.add_controller(resize_drag)

        self.create_canvas_context_menu()
        self.create_node_context_menu()

    def on_resize_drag_begin(self, gesture, x, y):
        if self.active_graph:
            for node in reversed(self.active_graph.nodes):
                if (x >= node.x + node.width - 10 and x <= node.x + node.width and
                        y >= node.y + node.height - 10 and y <= node.y + node.height):
                    self.resizing_node = node
                    self.initial_node_width = node.width
                    self.initial_node_height = node.height
                    gesture.set_state(Gtk.EventSequenceState.CLAIMED)
                    return

    def on_resize_drag_update(self, gesture, x, y):
        if self.resizing_node:
            offset_x, offset_y = gesture.get_offset()
            self.resizing_node.width = max(150, self.initial_node_width + offset_x)
            self.resizing_node.height = max(100, self.initial_node_height + offset_y)
            self.canvas.queue_draw()

    def on_resize_drag_end(self, gesture, x, y):
        if self.resizing_node:
            self.project_manager.set_dirty()
            self.resizing_node = None

    def on_canvas_draw(self, drawing_area, cr, width, height, data):
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
                start_x = self.connecting_from_node.x + self.connecting_from_node.width
                start_y = self.connecting_from_node.y + self.connecting_from_node.height / 2
                cr.set_source_rgb(0.8, 0.8, 0.2)
                cr.move_to(start_x, start_y)
                cr.line_to(self.connecting_line_x, self.connecting_line_y)
                cr.stroke()

    def draw_node(self, cr, node):
        # Node body
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.rectangle(node.x, node.y, node.width, node.height)
        cr.fill()

        # Node Header
        if isinstance(node, DialogueNode):
            cr.set_source_rgb(0.4, 0.6, 0.4)  # Greenish
        elif isinstance(node, ConditionNode):
            cr.set_source_rgb(0.6, 0.4, 0.4)  # Reddish
        elif isinstance(node, ActionNode):
            cr.set_source_rgb(0.4, 0.4, 0.6)  # Bluish
        else:
            cr.set_source_rgb(0.5, 0.5, 0.5)  # Grey
        cr.rectangle(node.x, node.y, node.width, 25)
        cr.fill()

        if node in self.selected_nodes:
            cr.set_source_rgb(1.0, 1.0, 0.0)  # Yellow for selection
            cr.set_line_width(3)
            cr.rectangle(node.x - 2, node.y - 2, node.width + 4, node.height + 4)
            cr.stroke()

        # Node text (using Pango)
        layout = PangoCairo.create_layout(cr)
        layout.set_width( (node.width - 20) * Pango.SCALE)
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)

        # Header text
        cr.set_source_rgb(1, 1, 1)
        header_text = f"<b>{node.node_type}</b>: {node.id}"
        layout.set_markup(header_text, -1)
        cr.move_to(node.x + 10, node.y + 5)
        PangoCairo.show_layout(cr, layout)

        # Body text
        text_x_offset = 10
        if isinstance(node, DialogueNode):
            character = next((c for c in self.project_manager.data.characters if c.id == node.character_id), None)
            if character and character.portrait_asset_id:
                asset = next((a for a in self.project_manager.data.assets if a.id == character.portrait_asset_id), None)
                if asset and asset.file_path:
                    full_path = os.path.join(self.project_manager.project_path, asset.file_path)
                    if os.path.exists(full_path):
                        try:
                            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(full_path, 64, 64, True)
                            Gdk.cairo_set_source_pixbuf(cr, pixbuf, node.x + 10, node.y + 30)
                            cr.paint()
                            text_x_offset = 84 # Indent text to make room for portrait
                        except Exception as e:
                            print(f"Error loading portrait: {e}")

        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.move_to(node.x + text_x_offset, node.y + 35)

        body_text = ""
        if isinstance(node, DialogueNode):
            body_text = f"<b>Char:</b> {node.character_id}\n<i>\"{node.dialogue_text}\"</i>"
        elif isinstance(node, ConditionNode):
            params_str = "\n".join([f"  - {k}: <i>{v}</i>" for k, v in node.parameters.items()])
            body_text = f"<b>If:</b> {node.condition_type}\n{params_str}"
        elif isinstance(node, ActionNode):
            params_str = "\n".join([f"  - {k}: <i>{v}</i>" for k, v in node.parameters.items()])
            body_text = f"<b>Do:</b> {node.action_command}\n{params_str}"

        layout.set_markup(body_text, -1)
        PangoCairo.show_layout(cr, layout)


        # Connectors
        connector_y = node.y + node.height / 2
        cr.set_source_rgb(0.8, 0.8, 0.2)
        # Input connector
        cr.rectangle(node.x - 5, connector_y - 5, 10, 10)
        cr.fill()
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.move_to(node.x - 25, connector_y + 5)
        cr.show_text("In")
        # Output connector
        cr.rectangle(node.x + node.width - 5, connector_y - 5, 10, 10)
        cr.fill()
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.move_to(node.x + node.width + 10, connector_y + 5)
        cr.show_text("Out")

        # Resize handle
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.rectangle(node.x + node.width - 10, node.y + node.height - 10, 10, 10)
        cr.fill()

    def draw_connection(self, cr, from_node, to_node):
        start_x = from_node.x + from_node.width
        start_y = from_node.y + from_node.height / 2
        end_x = to_node.x
        end_y = to_node.y + to_node.height / 2

        cr.set_source_rgb(0.8, 0.8, 0.2)
        cr.move_to(start_x, start_y)
        cr.curve_to(start_x + 50, start_y, end_x - 50, end_y, end_x, end_y)
        cr.stroke()

    def on_add_dialogue_node(self, button):
        if self.active_graph:
            new_node = DialogueNode(id=f"node_{len(self.active_graph.nodes)}", node_type="Dialogue", x=50, y=50)
            self.active_graph.nodes.append(new_node)
            self.canvas.queue_draw()
            self.minimap.queue_draw()
            self.project_manager.set_dirty()

    def on_add_condition_node(self, button):
        if self.active_graph:
            new_node = ConditionNode(id=f"node_{len(self.active_graph.nodes)}", node_type="Condition", x=50, y=50)
            self.active_graph.nodes.append(new_node)
            self.canvas.queue_draw()
            self.minimap.queue_draw()
            self.project_manager.set_dirty()

    def on_add_action_node(self, button, return_node=False):
        if self.active_graph:
            new_node = ActionNode(id=f"node_{len(self.active_graph.nodes)}", node_type="Action", x=50, y=50)
            self.active_graph.nodes.append(new_node)
            self.canvas.queue_draw()
            self.minimap.queue_draw()
            self.project_manager.set_dirty()
            if return_node:
                return new_node

    def on_drag_begin(self, gesture, x, y):
        if self.active_graph:
            for node in reversed(self.active_graph.nodes):
                # Check if the click is in the resize handle area (e.g., bottom-right 20x20 pixels)
                if (x >= node.x + node.width - 20 and x <= node.x + node.width and
                        y >= node.y + node.height - 20 and y <= node.y + node.height):
                    return  # Do not start a drag, let the resize gesture handle it

                if x >= node.x and x <= node.x + node.width and y >= node.y and y <= node.y + node.height:
                    self.dragging_node = node
                    if node not in self.selected_nodes:
                        self.selected_nodes = [node]

                    self.drag_offsets = {}
                    for n in self.selected_nodes:
                        self.drag_offsets[n.id] = (x - n.x, y - n.y)

                    gesture.set_state(Gtk.EventSequenceState.CLAIMED)
                    return

    def on_drag_update(self, gesture, x, y):
        if self.dragging_node:
            success, start_x, start_y = gesture.get_start_point()
            for node in self.selected_nodes:
                offset_x, offset_y = self.drag_offsets[node.id]
                node.x = start_x + x - offset_x
                node.y = start_y + y - offset_y
            self.canvas.queue_draw()
            self.minimap.queue_draw()

    def on_drag_end(self, gesture, x, y):
        if self.dragging_node:
            self.project_manager.set_dirty()
            self.dragging_node = None
            self.drag_offsets = {}

    def on_connection_drag_begin(self, gesture, x, y):
        if self.active_graph:
            for node in reversed(self.active_graph.nodes):
                connector_y = node.y + node.height / 2
                if x >= node.x + node.width - 5 and x <= node.x + node.width + 5 and y >= connector_y - 5 and y <= connector_y + 5:
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
        if self.connecting_from_node and self.active_graph:
            for node in reversed(self.active_graph.nodes):
                connector_y = node.y + node.height / 2
                if self.connecting_line_x >= node.x - 5 and self.connecting_line_x <= node.x + 5 and self.connecting_line_y >= connector_y - 5 and self.connecting_line_y <= connector_y + 5:
                    self.connecting_from_node.outputs.append(node.id)
                    node.inputs.append(self.connecting_from_node.id)
                    self.project_manager.set_dirty()
                    break
        self.connecting_from_node = None
        self.canvas.queue_draw()

    def on_canvas_click(self, gesture, n_press, x, y):
        node_clicked = None
        if self.active_graph:
            for node in self.active_graph.nodes:
                if x >= node.x and x <= node.x + node.width and y >= node.y and y <= node.y + node.height:
                    node_clicked = node
                    break

        if n_press == 2 and node_clicked:
            self.edit_node_dialog(node_clicked)
        elif n_press == 1:
            state = gesture.get_current_event_state()
            if not state & Gdk.ModifierType.SHIFT_MASK:
                self.selected_nodes.clear()

            if node_clicked:
                if node_clicked in self.selected_nodes:
                    self.selected_nodes.remove(node_clicked)
                else:
                    self.selected_nodes.append(node_clicked)

            self.delete_node_button.set_sensitive(len(self.selected_nodes) > 0)
            self.canvas.queue_draw()

    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Delete and self.selected_nodes:
            self.on_delete_node(None)
            return True
        return False

    def on_right_click(self, gesture, n_press, x, y):
        node_clicked = None
        if self.active_graph:
            for node in self.active_graph.nodes:
                if x >= node.x and x <= node.x + node.width and y >= node.y and y <= node.y + node.height:
                    node_clicked = node
                    break

        if node_clicked:
            self.selected_nodes = [node_clicked]
            self.node_context_menu.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
            self.node_context_menu.popup()
        else:
            self.canvas_context_menu.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
            self.canvas_context_menu.popup()

    def create_canvas_context_menu(self):
        menu = Gio.Menu.new()
        menu.append("Add Dialogue Node", "win.add-dialogue-node")
        menu.append("Add Condition Node", "win.add-condition-node")
        menu.append("Add Action Node", "win.add-action-node")
        self.canvas_context_menu = Gtk.PopoverMenu.new_from_model(menu)
        self.canvas_context_menu.set_parent(self.canvas)

    def create_node_context_menu(self):
        menu = Gio.Menu.new()
        menu.append("Edit Node", "win.edit-node")
        menu.append("Delete Node", "win.delete-node")

        section = Gio.Menu.new()
        section.append("Add Action", "win.add-action-to-dialogue")
        menu.append_section(None, section)

        self.node_context_menu = Gtk.PopoverMenu.new_from_model(menu)
        self.node_context_menu.set_parent(self.canvas)
