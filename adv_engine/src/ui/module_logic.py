import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
import json
from ..core.data_schemas import LogicNode, DialogueNode, ConditionNode, ActionNode, LogicGraph

class LogicEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.project_manager = project_manager
        self.dragging_node = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.active_graph = None
        self.selected_node = None
        self.connecting_from_node = None
        self.connecting_line_x = 0
        self.connecting_line_y = 0

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        if self.project_manager.data.logic_graphs:
            self.active_graph = self.project_manager.data.logic_graphs[0]
        else:
            self.active_graph = LogicGraph(id="default_graph", name="Default")
            self.project_manager.data.logic_graphs.append(self.active_graph)

        palette = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        palette.set_size_request(200, -1)

        dialogue_button = Gtk.Button(label="Add Dialogue")
        dialogue_button.connect("clicked", self.on_add_dialogue_node)
        palette.append(dialogue_button)
        condition_button = Gtk.Button(label="Add Condition")
        condition_button.connect("clicked", self.on_add_condition_node)
        palette.append(condition_button)
        action_button = Gtk.Button(label="Add Action")
        action_button.connect("clicked", self.on_add_action_node)
        palette.append(action_button)

        self.delete_node_button = Gtk.Button(label="Delete Node")
        self.delete_node_button.set_sensitive(False)
        self.delete_node_button.connect("clicked", self.on_delete_node)
        palette.append(self.delete_node_button)

        self.append(palette)

        self.canvas = Gtk.DrawingArea()
        self.canvas.set_hexpand(True)
        self.canvas.set_vexpand(True)
        self.canvas.set_draw_func(self.on_canvas_draw, None)
        self.canvas.set_focusable(True)
        self.append(self.canvas)

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
                start_x = self.connecting_from_node.x + 150
                start_y = self.connecting_from_node.y + 40
                cr.set_source_rgb(0.8, 0.8, 0.2)
                cr.move_to(start_x, start_y)
                cr.line_to(self.connecting_line_x, self.connecting_line_y)
                cr.stroke()

    def draw_node(self, cr, node):
        # Node body
        if isinstance(node, DialogueNode):
            cr.set_source_rgb(0.4, 0.6, 0.4)  # Greenish
        elif isinstance(node, ConditionNode):
            cr.set_source_rgb(0.6, 0.4, 0.4)  # Reddish
        elif isinstance(node, ActionNode):
            cr.set_source_rgb(0.4, 0.4, 0.6)  # Bluish
        else:
            cr.set_source_rgb(0.5, 0.5, 0.5)  # Grey
        cr.rectangle(node.x, node.y, 150, 80)
        cr.fill()

        if self.selected_node == node:
            cr.set_source_rgb(1.0, 1.0, 0.0)  # Yellow for selection
            cr.set_line_width(3)
            cr.rectangle(node.x - 2, node.y - 2, 154, 84)
            cr.stroke()

        # Node text
        cr.set_source_rgb(1, 1, 1)
        cr.move_to(node.x + 10, node.y + 20)
        cr.show_text(f"ID: {node.id}")
        cr.move_to(node.x + 10, node.y + 40)
        cr.show_text(f"Type: {node.node_type}")

        # Connectors
        cr.set_source_rgb(0.8, 0.8, 0.2)
        # Input connector
        cr.rectangle(node.x - 5, node.y + 35, 10, 10)
        cr.fill()
        # Output connector
        cr.rectangle(node.x + 145, node.y + 35, 10, 10)
        cr.fill()

    def draw_connection(self, cr, from_node, to_node):
        start_x = from_node.x + 150
        start_y = from_node.y + 40
        end_x = to_node.x
        end_y = to_node.y + 40

        cr.set_source_rgb(0.8, 0.8, 0.2)
        cr.move_to(start_x, start_y)

        # Control points for the Bézier curve
        c1_x = start_x + 50
        c1_y = start_y
        c2_x = end_x - 50
        c2_y = end_y

        cr.curve_to(c1_x, c1_y, c2_x, c2_y, end_x, end_y)
        cr.stroke()

    def on_add_dialogue_node(self, button):
        if self.active_graph:
            new_node = DialogueNode(id=f"node_{len(self.active_graph.nodes)}", node_type="Dialogue", x=50, y=50)
            self.active_graph.nodes.append(new_node)
            self.canvas.queue_draw()
            self.project_manager.save_project()

    def on_add_condition_node(self, button):
        if self.active_graph:
            new_node = ConditionNode(id=f"node_{len(self.active_graph.nodes)}", node_type="Condition", x=50, y=50)
            self.active_graph.nodes.append(new_node)
            self.canvas.queue_draw()
            self.project_manager.save_project()

    def on_add_action_node(self, button):
        if self.active_graph:
            new_node = ActionNode(id=f"node_{len(self.active_graph.nodes)}", node_type="Action", x=50, y=50)
            self.active_graph.nodes.append(new_node)
            self.canvas.queue_draw()
            self.project_manager.save_project()

    def on_drag_begin(self, gesture, x, y):
        if self.active_graph:
            for node in reversed(self.active_graph.nodes):
                if x >= node.x and x <= node.x + 150 and y >= node.y and y <= node.y + 80:
                    self.dragging_node = node
                    self.drag_offset_x = x - node.x
                    self.drag_offset_y = y - node.y
                    gesture.set_state(Gtk.EventSequenceState.CLAIMED)
                    return

    def on_drag_update(self, gesture, x, y):
        if self.dragging_node:
            success, start_x, start_y = gesture.get_start_point()
            self.dragging_node.x = start_x + x - self.drag_offset_x
            self.dragging_node.y = start_y + y - self.drag_offset_y
            self.canvas.queue_draw()

    def on_drag_end(self, gesture, x, y):
        if self.dragging_node:
            self.project_manager.save_project()
            self.dragging_node = None

    def on_connection_drag_begin(self, gesture, x, y):
        if self.active_graph:
            for node in reversed(self.active_graph.nodes):
                if x >= node.x + 145 and x <= node.x + 155 and y >= node.y + 35 and y <= node.y + 45:
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
                if self.connecting_line_x >= node.x - 5 and self.connecting_line_x <= node.x + 5 and self.connecting_line_y >= node.y + 35 and self.connecting_line_y <= node.y + 45:
                    self.connecting_from_node.outputs.append(node.id)
                    node.inputs.append(self.connecting_from_node.id)
                    self.project_manager.save_project()
                    break
        self.connecting_from_node = None
        self.canvas.queue_draw()

    def on_canvas_click(self, gesture, n_press, x, y):
        node_clicked = None
        if self.active_graph:
            for node in self.active_graph.nodes:
                if x >= node.x and x <= node.x + 150 and y >= node.y and y <= node.y + 80:
                    node_clicked = node
                    break

        if n_press == 2 and node_clicked:
            self.edit_node_dialog(node_clicked)
        elif n_press == 1:
            self.selected_node = node_clicked
            self.delete_node_button.set_sensitive(self.selected_node is not None)
            self.canvas.queue_draw()

    def edit_node_dialog(self, node):
        dialog = Gtk.Dialog(title=f"Edit Node {node.id}", transient_for=self.get_native(), modal=True)
        dialog.add_buttons("_Cancel", Gtk.ResponseType.CANCEL, "_Save", Gtk.ResponseType.OK)
        content_area = dialog.get_content_area()
        content_area.set_spacing(10)

        entries = {}

        if isinstance(node, DialogueNode):
            content_area.append(Gtk.Label(label="Character ID:", halign=Gtk.Align.START))
            char_id_entry = Gtk.Entry(text=node.character_id)
            entries['character_id'] = char_id_entry
            content_area.append(char_id_entry)

            content_area.append(Gtk.Label(label="Dialogue Text:", halign=Gtk.Align.START))
            dialogue_text_entry = Gtk.Entry(text=node.dialogue_text)
            entries['dialogue_text'] = dialogue_text_entry
            content_area.append(dialogue_text_entry)

        elif isinstance(node, ConditionNode):
            content_area.append(Gtk.Label(label="Condition Type:", halign=Gtk.Align.START))
            condition_type_entry = Gtk.Entry(text=node.condition_type)
            entries['condition_type'] = condition_type_entry
            content_area.append(condition_type_entry)

            content_area.append(Gtk.Label(label="Parameters (JSON):", halign=Gtk.Align.START))
            parameters_entry = Gtk.Entry(text=json.dumps(node.parameters))
            entries['parameters'] = parameters_entry
            content_area.append(parameters_entry)

        elif isinstance(node, ActionNode):
            content_area.append(Gtk.Label(label="Action Command:", halign=Gtk.Align.START))
            action_command_entry = Gtk.Entry(text=node.action_command)
            entries['action_command'] = action_command_entry
            content_area.append(action_command_entry)

            content_area.append(Gtk.Label(label="Parameters (JSON):", halign=Gtk.Align.START))
            parameters_entry = Gtk.Entry(text=json.dumps(node.parameters))
            entries['parameters'] = parameters_entry
            content_area.append(parameters_entry)

        def on_response(dialog, response_id):
            if response_id == Gtk.ResponseType.OK:
                try:
                    if isinstance(node, DialogueNode):
                        node.character_id = entries['character_id'].get_text()
                        node.dialogue_text = entries['dialogue_text'].get_text()
                    elif isinstance(node, ConditionNode):
                        node.condition_type = entries['condition_type'].get_text()
                        node.parameters = json.loads(entries['parameters'].get_text())
                    elif isinstance(node, ActionNode):
                        node.action_command = entries['action_command'].get_text()
                        node.parameters = json.loads(entries['parameters'].get_text())

                    self.project_manager.save_project()
                    self.canvas.queue_draw()
                except json.JSONDecodeError:
                    print("Error: Invalid JSON in parameters")
                except Exception as e:
                    print(f"An error occurred: {e}")
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.show()

    def on_delete_node(self, button):
        if self.selected_node and self.active_graph:
            node_to_delete = self.selected_node
            self.active_graph.nodes.remove(node_to_delete)

            # Remove any connections to the deleted node
            for node in self.active_graph.nodes:
                if node_to_delete.id in node.outputs:
                    node.outputs.remove(node_to_delete.id)
                if node_to_delete.id in node.inputs:
                    node.inputs.remove(node_to_delete.id)

            self.selected_node = None
            self.delete_node_button.set_sensitive(False)
            self.project_manager.save_project()
            self.canvas.queue_draw()

    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Delete and self.selected_node:
            self.on_delete_node(None)
            return True
        return False
