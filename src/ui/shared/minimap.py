"""A minimap widget for the logic editor."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class MiniMap(Gtk.DrawingArea):
    """A minimap widget that displays a scaled-down view of the logic canvas.

    Attributes:
        logic_editor_canvas: A reference to the main LogicEditor canvas.
    """

    def __init__(self, **kwargs):
        """Initializes a new MiniMap instance.

        Args:
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.logic_editor_canvas = None
        self.set_draw_func(self.on_draw, None)
        self.set_size_request(200, 150)

    def set_canvas(self, canvas):
        """Sets the canvas for the minimap.

        Args:
            canvas (LogicEditor): The logic editor canvas.
        """
        self.logic_editor_canvas = canvas

    def on_draw(self, drawing_area, cr, width, height, data):
        """Draws the minimap content on the drawing area.

        Args:
            drawing_area (Gtk.DrawingArea): The drawing area.
            cr: The Cairo context.
            width (int): The width of the drawing area.
            height (int): The height of the drawing area.
            data: User data (unused).
        """
        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.paint()

        if not self.logic_editor_canvas:
            return

        active_graph = self.logic_editor_canvas.active_graph
        if not active_graph or not active_graph.nodes:
            return

        min_x = min(node.x for node in active_graph.nodes)
        min_y = min(node.y for node in active_graph.nodes)
        max_x = max(node.x + node.width for node in active_graph.nodes)
        max_y = max(node.y + node.height for node in active_graph.nodes)

        graph_width = max_x - min_x
        graph_height = max_y - min_y

        if graph_width == 0 or graph_height == 0:
            return

        scale = min(width / graph_width, height / graph_height) * 0.9
        offset_x = (width - (graph_width * scale)) / 2 - (min_x * scale)
        offset_y = (height - (graph_height * scale)) / 2 - (min_y * scale)

        for node in active_graph.nodes:
            cr.set_source_rgb(0.5, 0.5, 0.5)
            cr.rectangle(
                node.x * scale + offset_x,
                node.y * scale + offset_y,
                node.width * scale,
                node.height * scale,
            )
            cr.fill()
