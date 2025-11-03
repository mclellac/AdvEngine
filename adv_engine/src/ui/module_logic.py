import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from ..core.data_schemas import LogicNode, DialogueNode, ConditionNode, ActionNode, LogicGraph

class LogicEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.project_manager = project_manager
        self.dragging_node = None
        self.active_graph = None

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        # For this example, we'll just work on the first graph if it exists.
        if self.project_manager.data.logic_graphs:
            self.active_graph = self.project_manager.data.logic_graphs[0]
        else:
            # Create a default graph if none exist
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

        self.append(palette)

        self.canvas = Gtk.DrawingArea()
        self.canvas.set_hexpand(True)
        self.canvas.set_vexpand(True)
        self.canvas.set_draw_func(self.on_canvas_draw, None)
        self.append(self.canvas)

        drag = Gtk.GestureDrag.new()
        drag.connect("drag-begin", self.on_drag_begin)
        drag.connect("drag-update", self.on_drag_update)
        drag.connect("drag-end", self.on_drag_end)
        self.canvas.add_controller(drag)

    def on_canvas_draw(self, drawing_area, cr, width, height, data):
        cr.set_source_rgb(0.15, 0.15, 0.15)
        cr.paint()
        if self.active_graph:
            for node in self.active_graph.nodes:
                self.draw_node(cr, node)

    def draw_node(self, cr, node):
        cr.set_source_rgb(0.4, 0.4, 0.6)
        cr.rectangle(node.x, node.y, 150, 80)
        cr.fill()

        cr.set_source_rgb(1, 1, 1)
        cr.move_to(node.x + 10, node.y + 20)
        cr.show_text(f"ID: {node.id}")
        cr.move_to(node.x + 10, node.y + 40)
        cr.show_text(f"Type: {node.node_type}")

    def on_add_dialogue_node(self, button):
        if self.active_graph:
            new_node = DialogueNode(id=f"node_{len(self.active_graph.nodes)}", node_type="Dialogue", x=50, y=50, character_id="", dialogue_text="")
            self.active_graph.nodes.append(new_node)
            self.canvas.queue_draw()
            self.project_manager.save_project()

    def on_add_condition_node(self, button):
        if self.active_graph:
            new_node = ConditionNode(id=f"node_{len(self.active_graph.nodes)}", node_type="Condition", x=50, y=50, condition_type="", parameters={})
            self.active_graph.nodes.append(new_node)
            self.canvas.queue_draw()
            self.project_manager.save_project()

    def on_add_action_node(self, button):
        if self.active_graph:
            new_node = ActionNode(id=f"node_{len(self.active_graph.nodes)}", node_type="Action", x=50, y=50, action_command="", parameters={})
            self.active_graph.nodes.append(new_node)
            self.canvas.queue_draw()
            self.project_manager.save_project()

    def on_drag_begin(self, gesture, x, y):
        if self.active_graph:
            for node in reversed(self.active_graph.nodes):
                if x >= node.x and x <= node.x + 150 and y >= node.y and y <= node.y + 80:
                    self.dragging_node = node
                    gesture.set_state(Gtk.EventSequenceState.CLAIMED)
                    return

    def on_drag_update(self, gesture, x, y):
        if self.dragging_node:
            self.dragging_node.x += x
            self.dragging_node.y += y
            self.canvas.queue_draw()

    def on_drag_end(self, gesture, x, y):
        if self.dragging_node:
            self.project_manager.save_project()
            self.dragging_node = None
