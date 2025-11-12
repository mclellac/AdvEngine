"""The logic editor for the AdvEngine application.

This module defines the LogicEditor, a node-based graphical interface for
scripting game logic. It includes the main editor canvas, a tool palette,
a properties panel for editing nodes, and a minimap for navigation.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw, Gio, PangoCairo, Pango, GLib
from ..core.schemas.logic import (
    ActionNode,
    ConditionNode,
    DialogueNode,
    LogicGraph,
    LogicNode,
)
from ..core.ue_exporter import get_command_definitions
from .shared.dynamic_node_editor import DynamicNodeEditor
from .shared.minimap import MiniMap


@Gtk.Template(resource_path="/com/github/mclellac/AdvEngine/ui/logic_editor.ui")
class LogicEditor(Adw.Bin):
    """The main logic editor widget.

    This editor provides a canvas for creating and editing logic graphs, a
    tool palette for adding new nodes, and a properties panel for editing
    the selected node.

    Attributes:
        project_manager: The main project manager instance.
        settings_manager: The main settings manager instance.
        active_graph (LogicGraph): The currently active logic graph.
        selected_nodes (list[LogicNode]): A list of the currently selected
            nodes.
    """

    __gtype_name__ = "LogicEditor"

    EDITOR_NAME = "Logic"
    VIEW_NAME = "logic_editor"
    ORDER = 1

    canvas = Gtk.Template.Child()
    canvas_stack = Gtk.Template.Child()
    minimap = Gtk.Template.Child()
    props_panel = Gtk.Template.Child()
    add_dialogue_node_button = Gtk.Template.Child()
    add_condition_node_button = Gtk.Template.Child()
    add_action_node_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Initializes a new LogicEditor instance.

        Args:
            **kwargs: Additional keyword arguments.
        """
        project_manager = kwargs.pop("project_manager")
        settings_manager = kwargs.pop("settings_manager")

        super().__init__(**kwargs)
        self.init_template()

        self.project_manager = project_manager
        self.settings_manager = settings_manager
        self.active_graph = None
        self.selected_nodes = []
        self.drag_mode = None  # None, 'dragging', 'connecting', 'resizing', 'selecting'
        self.connecting_from_node = None
        self.connecting_line_pos = (0, 0)
        self.resizing_node = None
        self.drag_selection_rect = None

        self.drag_offsets = {}
        self.initial_node_size = (0, 0)

        self.canvas.set_draw_func(self.on_canvas_draw, None)
        self._setup_canvas_controllers()
        self._create_context_menus()
        self.project_manager.register_project_loaded_callback(self.project_loaded)

        self.minimap.set_canvas(self)
        self.props_panel.set_managers(self.project_manager, self.settings_manager)
        self.props_panel.set_on_update_callback(self.update_node_and_redraw)

        self.add_dialogue_node_button.connect(
            "clicked", lambda _: self.on_add_node(DialogueNode, "Dialogue")
        )
        self.add_condition_node_button.connect(
            "clicked", lambda _: self.on_add_node(ConditionNode, "Condition")
        )
        self.add_action_node_button.connect(
            "clicked", lambda _: self.on_add_node(ActionNode, "Action")
        )

    def project_loaded(self):
        """Callback for when the project is loaded."""
        if self.project_manager.data.logic_graphs:
            self.active_graph = self.project_manager.data.logic_graphs[0]
        else:
            self.active_graph = LogicGraph(id="default_graph", name="Default")
            self.project_manager.data.logic_graphs.append(self.active_graph)

        # Always show the canvas, even if the graph is empty.
        self.canvas_stack.set_visible_child_name("canvas")
        self.canvas.queue_draw()
        self.minimap.queue_draw()

    def _setup_canvas_controllers(self):
        """Sets up the event controllers for the main canvas."""
        drag_gesture = Gtk.GestureDrag.new()
        drag_gesture.connect("drag-begin", self.on_drag_begin)
        drag_gesture.connect("drag-update", self.on_drag_update)
        drag_gesture.connect("drag-end", self.on_drag_end)
        self.canvas.add_controller(drag_gesture)

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

    def _create_context_menus(self):
        """Creates the context menus for the canvas and nodes."""
        menu = Gio.Menu.new()
        menu.append("Add Dialogue Node", "app.add_dialogue_node")
        menu.append("Add Condition Node", "app.add_condition_node")
        menu.append("Add Action Node", "app.add_action_node")
        self.canvas_context_menu = Gtk.PopoverMenu.new_from_model(menu)
        self.canvas_context_menu.set_parent(self.canvas)

        menu = Gio.Menu.new()
        menu.append("Delete Node", "app.delete_node")
        self.node_context_menu = Gtk.PopoverMenu.new_from_model(menu)
        self.node_context_menu.set_parent(self.canvas)

    def on_canvas_draw(self, area, cr, w, h, _):
        """Draws the content of the logic editor canvas.

        Args:
            area (Gtk.DrawingArea): The drawing area.
            cr: The Cairo context.
            w (int): The width of the drawing area.
            h (int): The height of the drawing area.
            _: User data (unused).
        """
        cr.set_source_rgb(0.15, 0.15, 0.15)
        cr.paint()
        if self.active_graph:
            if not self.active_graph.nodes:
                # If there are no nodes, draw a helpful message on the canvas
                layout = PangoCairo.create_layout(cr)
                layout.set_width(w * Pango.SCALE)
                layout.set_alignment(Pango.Alignment.CENTER)
                cr.set_source_rgb(0.7, 0.7, 0.7)
                layout.set_markup(
                    "No nodes yet. Right-click or use the Tool Palette to add one."
                )
                cr.move_to(0, h / 2 - 50)
                PangoCairo.show_layout(cr, layout)

            for node in self.active_graph.nodes:
                self.draw_node(cr, node)
                for output_node_id in node.outputs:
                    output_node = next(
                        (n for n in self.active_graph.nodes if n.id == output_node_id),
                        None,
                    )
                    if output_node:
                        self.draw_connection(cr, node, output_node)
            if self.drag_mode == "connecting" and self.connecting_from_node:
                start_x, start_y = self.get_connector_pos(
                    self.connecting_from_node, "out"
                )
                end_x, end_y = self.connecting_line_pos
                cr.set_source_rgb(0.8, 0.8, 0.2)
                cr.move_to(start_x, start_y)
                cr.line_to(end_x, end_y)
                cr.stroke()
            if self.drag_mode == "selecting" and self.drag_selection_rect:
                cr.set_source_rgba(0.2, 0.5, 1.0, 0.3)
                x1, y1, x2, y2 = self.drag_selection_rect
                cr.rectangle(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))
                cr.fill()

    def draw_node(self, cr, node):
        """Draws a single node on the canvas.

        Args:
            cr: The Cairo context.
            node (LogicNode): The node to draw.
        """
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.rectangle(node.x, node.y, node.width, node.height)
        cr.fill()

        if isinstance(node, DialogueNode):
            cr.set_source_rgb(0.4, 0.6, 0.4)
        elif isinstance(node, ConditionNode):
            cr.set_source_rgb(0.6, 0.4, 0.4)
        elif isinstance(node, ActionNode):
            cr.set_source_rgb(0.4, 0.4, 0.6)
        else:
            cr.set_source_rgb(0.5, 0.5, 0.5)
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
        if not hasattr(node, "body_text") or node.body_text is None:
            self.update_node_body_text(node)
        layout.set_markup(node.body_text or "", -1)
        PangoCairo.show_layout(cr, layout)

        self.draw_connectors_and_resize_handle(cr, node)

    def update_node_body_text(self, node: LogicNode):
        """Updates the cached body text for a node.

        Args:
            node (LogicNode): The node to update.
        """
        body_text = ""
        if isinstance(node, DialogueNode):
            body_text = (
                f'<b>Char:</b> {node.character_id}\n<i>"{node.dialogue_text}"</i>'
            )
        elif isinstance(node, ConditionNode):
            body_text = f"<b>IF</b> {node.condition_type}\n"
            if node.condition_type == "VARIABLE_EQUALS":
                body_text += f"  {node.var_name} == {node.value}"
            elif node.condition_type == "HAS_ITEM":
                body_text += f"  Player has {node.amount} of {node.item_id}"
            elif node.condition_type == "ATTRIBUTE_CHECK":
                body_text += f"  {node.attribute_id} {node.comparison} {node.value}"
            else:
                body_text += "<i>(Condition details not yet formatted)</i>"

        elif isinstance(node, ActionNode):
            body_text = f"<b>DO</b> {node.action_command}\n"
            defs = get_command_definitions()["actions"]
            if node.action_command in defs:
                params = defs[node.action_command]["params"]
                param_strings = []
                for param, p_type in params.items():
                    param_snake_case = pascal_to_snake(param)
                    value = getattr(node, param_snake_case, "")
                    param_strings.append(f"{param}: {value}")
                body_text += f"  ({', '.join(param_strings)})"
        node.body_text = body_text

    def update_node_and_redraw(self):
        """Callback to update the selected nodes and redraw the canvas."""
        if self.selected_nodes:
            for node in self.selected_nodes:
                self.update_node_body_text(node)
            self.canvas.queue_draw()

    def draw_connectors_and_resize_handle(self, cr, node: LogicNode):
        """Draws the input/output connectors and resize handle for a node.

        Args:
            cr: The Cairo context.
            node (LogicNode): The node to draw connectors for.
        """
        connector_y = node.y + node.height / 2
        cr.set_source_rgb(0.8, 0.8, 0.2)
        cr.rectangle(node.x - 5, connector_y - 5, 10, 10)
        cr.rectangle(node.x + node.width - 5, connector_y - 5, 10, 10)
        cr.fill()
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.rectangle(node.x + node.width - 10, node.y + node.height - 10, 10, 10)
        cr.fill()

    def draw_connection(self, cr, from_node: LogicNode, to_node: LogicNode):
        """Draws a Bezier curve connection between two nodes.

        Args:
            cr: The Cairo context.
            from_node (LogicNode): The node the connection starts from.
            to_node (LogicNode): The node the connection ends at.
        """
        start_x, start_y = self.get_connector_pos(from_node, "out")
        end_x, end_y = self.get_connector_pos(to_node, "in")
        cr.set_source_rgb(0.8, 0.8, 0.2)
        cr.move_to(start_x, start_y)
        cr.curve_to(start_x + 50, start_y, end_x - 50, end_y, end_x, end_y)
        cr.stroke()

    def on_add_node(self, node_class: type, node_type: str):
        """Handles adding a new node to the canvas.

        Args:
            node_class (type): The class of the node to create.
            node_type (str): The type identifier for the new node.
        """
        if self.active_graph:
            new_id = f"node_{len(self.active_graph.nodes)}"
            existing_ids = {node.id for node in self.active_graph.nodes}
            count = 0
            while new_id in existing_ids:
                new_id = f"node_{len(self.active_graph.nodes)}_{count}"
                count += 1

            node_width = self.settings_manager.get("default_node_width", 240)
            node_height = self.settings_manager.get("default_node_height", 160)
            new_node = node_class(
                id=new_id,
                node_type=node_type,
                x=50,
                y=50,
                width=node_width,
                height=node_height,
            )
            self.active_graph.nodes.append(new_node)
            self.canvas.queue_draw()
            if hasattr(self, "minimap"):
                self.minimap.queue_draw()
            self.project_manager.set_dirty(True)

    def get_connector_pos(self, node: LogicNode, connector_type: str) -> tuple[int, int]:
        """Gets the position of a connector on a node.

        Args:
            node (LogicNode): The node.
            connector_type (str): 'in' or 'out'.

        Returns:
            tuple[int, int]: The (x, y) coordinates of the connector.
        """
        if connector_type == "in":
            return node.x, node.y + node.height / 2
        else:
            return node.x + node.width, node.y + node.height / 2

    def on_drag_begin(self, gesture: Gtk.GestureDrag, x: float, y: float):
        """Handles the beginning of a drag operation on the canvas.

        Args:
            gesture (Gtk.GestureDrag): The drag gesture.
            x (float): The x-coordinate of the drag start.
            y (float): The y-coordinate of the drag start.
        """
        self.drag_mode = None
        for node in reversed(self.active_graph.nodes if self.active_graph else []):
            # Check for resize handle
            if (
                x >= node.x + node.width - 15
                and y >= node.y + node.height - 15
            ):
                self.drag_mode = "resizing"
                self.resizing_node = node
                self.initial_node_size = (node.width, node.height)
                gesture.set_state(Gtk.EventSequenceState.CLAIMED)
                return

            # Check for output connector
            out_x, out_y = self.get_connector_pos(node, "out")
            if abs(x - out_x) < 10 and abs(y - out_y) < 10:
                self.drag_mode = "connecting"
                self.connecting_from_node = node
                self.connecting_line_pos = (x, y)
                gesture.set_state(Gtk.EventSequenceState.CLAIMED)
                return

        # Check for node drag
        node_clicked = self.get_node_at(x, y)
        if node_clicked:
            self.drag_mode = "dragging"
            if node_clicked not in self.selected_nodes:
                # If not multi-selecting, start a new selection
                if not gesture.get_current_event_state() & Gdk.ModifierType.SHIFT_MASK:
                    self.selected_nodes = [node_clicked]
                else:
                    self.selected_nodes.append(node_clicked)

            self.props_panel.set_node(
                self.selected_nodes[0] if len(self.selected_nodes) == 1 else None
            )

            self.drag_offsets = {n.id: (x - n.x, y - n.y) for n in self.selected_nodes}
            gesture.set_state(Gtk.EventSequenceState.CLAIMED)
            return

        # If nothing else, start selection rectangle
        self.drag_mode = "selecting"
        self.drag_selection_rect = [x, y, x, y]
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)

    def on_drag_update(self, gesture: Gtk.GestureDrag, x: float, y: float):
        """Handles the update of a drag operation.

        Args:
            gesture (Gtk.GestureDrag): The drag gesture.
            x (float): The x-offset of the drag.
            y (float): The y-offset of the drag.
        """
        success, start_x, start_y = gesture.get_start_point()
        if not success:
            return

        if self.drag_mode == "dragging":
            for node in self.selected_nodes:
                offset_x, offset_y = self.drag_offsets[node.id]
                new_x = start_x + x - offset_x
                new_y = start_y + y - offset_y

                if self.settings_manager.get("grid_snap_enabled", True):
                    grid_size = self.settings_manager.get("grid_size", 20)
                    new_x = round(new_x / grid_size) * grid_size
                    new_y = round(new_y / grid_size) * grid_size

                node.x = new_x
                node.y = new_y
            self.canvas.queue_draw()
        elif self.drag_mode == "selecting":
            if self.drag_selection_rect:
                self.drag_selection_rect[2] = start_x + x
                self.drag_selection_rect[3] = start_y + y
                self.canvas.queue_draw()
        elif self.drag_mode == "connecting":
            self.connecting_line_pos = (start_x + x, start_y + y)
            self.canvas.queue_draw()
        elif self.drag_mode == "resizing" and self.resizing_node:
            initial_width, initial_height = self.initial_node_size
            self.resizing_node.width = max(150, initial_width + x)
            self.resizing_node.height = max(100, initial_height + y)
            self.canvas.queue_draw()

    def on_drag_end(self, gesture: Gtk.GestureDrag, x: float, y: float):
        """Handles the end of a drag operation.

        Args:
            gesture (Gtk.GestureDrag): The drag gesture.
            x (float): The x-offset of the drag end.
            y (float): The y-offset of the drag end.
        """
        if self.drag_mode == "dragging":
            self.project_manager.set_dirty(True)
        elif self.drag_mode == "selecting" and self.drag_selection_rect:
            self.selected_nodes.clear()
            x1, y1, x2, y2 = self.drag_selection_rect
            rect = Gdk.Rectangle()
            rect.x = min(x1, x2)
            rect.y = min(y1, y2)
            rect.width = abs(x1 - x2)
            rect.height = abs(y1 - y2)
            if self.active_graph:
                for node in self.active_graph.nodes:
                    node_rect = Gdk.Rectangle()
                    node_rect.x, node_rect.y, node_rect.width, node_rect.height = (
                        node.x,
                        node.y,
                        node.width,
                        node.height,
                    )
                    if rect.intersect(node_rect)[0]:
                        self.selected_nodes.append(node)
            self.canvas.queue_draw()
        elif self.drag_mode == "connecting" and self.connecting_from_node:
            end_x, end_y = self.connecting_line_pos
            target_node = self.get_node_at(end_x, end_y)
            if target_node and target_node != self.connecting_from_node:
                in_x, in_y = self.get_connector_pos(target_node, "in")
                if abs(end_x - in_x) < 10 and abs(end_y - in_y) < 10:
                    self.connecting_from_node.outputs.append(target_node.id)
                    target_node.inputs.append(self.connecting_from_node.id)
                    self.project_manager.set_dirty(True)
            self.canvas.queue_draw()
        elif self.drag_mode == "resizing":
            self.project_manager.set_dirty(True)

        # Reset state
        self.drag_mode = None
        self.drag_offsets = {}
        self.drag_selection_rect = None
        self.connecting_from_node = None
        self.resizing_node = None

    def on_canvas_click(self, gesture: Gtk.GestureClick, n_press: int, x: float, y: float):
        """Handles a click event on the canvas.

        Args:
            gesture (Gtk.GestureClick): The click gesture.
            n_press (int): The number of presses.
            x (float): The x-coordinate of the click.
            y (float): The y-coordinate of the click.
        """
        node = self.get_node_at(x, y)
        if node:
            if not gesture.get_current_event_state() & Gdk.ModifierType.SHIFT_MASK:
                self.selected_nodes = [node]
            else:
                if node in self.selected_nodes:
                    self.selected_nodes.remove(node)
                else:
                    self.selected_nodes.append(node)
        else:
            self.selected_nodes = []
        self.props_panel.set_node(
            self.selected_nodes[0] if len(self.selected_nodes) == 1 else None
        )
        self.canvas.queue_draw()

    def on_key_pressed(self, controller, keyval, keycode, state):
        """Handles a key-pressed event on the canvas.

        Args:
            controller: The event controller.
            keyval: The key value.
            keycode: The key code.
            state: The modifier state.
        """
        if keyval == Gdk.KEY_Delete:
            if not self.active_graph:
                return
            for node_to_delete in self.selected_nodes:
                self.active_graph.nodes.remove(node_to_delete)
                # Also remove any connections pointing to the deleted node
                for node in self.active_graph.nodes:
                    if node_to_delete.id in node.outputs:
                        node.outputs.remove(node_to_delete.id)
            self.selected_nodes.clear()
            self.props_panel.set_node(None)
            self.canvas.queue_draw()
            self.project_manager.set_dirty(True)

    def get_node_at(self, x: float, y: float) -> LogicNode | None:
        """Gets the topmost node at the given coordinates.

        Args:
            x (float): The x-coordinate.
            y (float): The y-coordinate.

        Returns:
            LogicNode or None: The node at the given coordinates, or None if
            no node is found.
        """
        if self.active_graph:
            for node in reversed(self.active_graph.nodes):
                if (
                    x >= node.x
                    and x <= node.x + node.width
                    and y >= node.y
                    and y <= node.y + node.height
                ):
                    return node
        return None

    def on_right_click(self, gesture: Gtk.GestureClick, n_press: int, x: float, y: float):
        """Handles a right-click on the canvas to show a context menu.

        Args:
            gesture (Gtk.GestureClick): The click gesture.
            n_press (int): The number of presses.
            x (float): The x-coordinate of the click.
            y (float): The y-coordinate of the click.
        """
        node = self.get_node_at(x, y)
        if node:
            self.selected_nodes = [node]
            self.node_context_menu.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
            self.node_context_menu.popup()
        else:
            self.canvas_context_menu.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
            self.canvas_context_menu.popup()
