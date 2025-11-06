"""The dialogue editor for the AdvEngine application."""

import os
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject, Gio
from ..core.data_schemas import DialogueNode, ActionNode, LogicGraph
from .module_logic import DynamicNodeEditor


class DialogueNodeGObject(GObject.Object):
    """GObject wrapper for the DialogueNode and ActionNode dataclasses."""
    __gtype_name__ = 'DialogueNodeGObject'

    id = GObject.Property(type=str)
    node_type = GObject.Property(type=str)
    display_text = GObject.Property(type=str)

    def __init__(self, node):
        """Initializes a new DialogueNodeGObject instance."""
        super().__init__()
        self.node = node
        self.id = node.id
        self.node_type = node.node_type

        if isinstance(node, DialogueNode):
            self.display_text = f"{node.character_id}: {node.dialogue_text[:30]}..."
        elif isinstance(node, ActionNode):
            self.display_text = f"-> ACTION: {node.action_command}"


class DialogueEditor(Adw.Bin):
    """A widget for editing dialogue trees.

    This editor provides a tree view of the dialogue graph, a properties
    panel for editing the selected node, and buttons for adding and deleting
    nodes.
    """
    EDITOR_NAME = "Dialogue"
    VIEW_NAME = "dialogue_editor"
    ORDER = 3

    def __init__(self, project_manager, **kwargs):
        """Initializes a new DialogueEditor instance.

        Args:
            project_manager: The project manager instance.
        """
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.active_graph = None

        root_widget = self._build_ui()
        self.set_child(root_widget)

        self._load_dialogue_graphs()

    def _build_ui(self):
        """Builds the user interface for the editor."""
        root_box = Gtk.Box()
        paned = Adw.OverlaySplitView()
        paned.set_sidebar(self._create_tree_panel())
        paned.set_content(self._create_properties_panel())
        root_box.append(paned)
        return root_box

    def _create_tree_panel(self):
        """Creates the panel with the dialogue tree."""
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        left_box.append(toolbar)

        self.add_dialogue_button = Gtk.Button(label="Add Dialogue")
        self.add_dialogue_button.connect("clicked", self._on_add_dialogue_node)
        toolbar.append(self.add_dialogue_button)

        self.add_action_button = Gtk.Button(label="Add Action")
        self.add_action_button.connect("clicked", self._on_add_action_node)
        toolbar.append(self.add_action_button)

        self.delete_button = Gtk.Button(label="Delete")
        self.delete_button.set_sensitive(False)
        self.delete_button.connect("clicked", self._on_delete_node)
        toolbar.append(self.delete_button)

        self.model = Gio.ListStore(item_type=DialogueNodeGObject)
        self.tree_model = Gtk.TreeListModel.new(
            self.model, passthrough=False, autoexpand=True, create_func=self._get_children)

        self.selection = Gtk.SingleSelection(model=self.tree_model)
        self.selection.connect("selection-changed", self._on_selection_changed)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_list_item)
        factory.connect("bind", self._bind_list_item)

        list_view = Gtk.ListView(model=self.selection, factory=factory)
        list_view_scrolled = Gtk.ScrolledWindow()
        list_view_scrolled.set_child(list_view)
        left_box.append(list_view_scrolled)

        return left_box

    def _create_properties_panel(self):
        """Creates the panel for editing the properties of the selected node."""
        self.properties_stack = Gtk.Stack()
        self.properties_stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        self.placeholder = Adw.StatusPage(
            title="Select a node to edit its properties.")
        self.properties_stack.add_named(self.placeholder, "placeholder")

        self.dialogue_node_editor = DynamicNodeEditor(
            project_manager=self.project_manager)
        self.properties_stack.add_named(
            self.dialogue_node_editor, "editor")

        self.properties_stack.set_visible_child_name("placeholder")
        return self.properties_stack

    def _get_children(self, item):
        """Gets the children of a node in the dialogue tree."""
        node = item.node
        if isinstance(node, DialogueNode):
            children = Gio.ListStore(item_type=DialogueNodeGObject)
            for child_id in node.outputs:
                child_node = next(
                    (n for n in self.active_graph.nodes if n.id == child_id), None)
                if child_node:
                    children.append(DialogueNodeGObject(child_node))
            return children
        return None

    def _setup_list_item(self, factory, list_item):
        """Sets up a list item in the dialogue tree."""
        label = Gtk.Label(halign=Gtk.Align.START)
        list_item.set_child(label)

    def _bind_list_item(self, factory, list_item):
        """Binds a list item to the data model."""
        label = list_item.get_child()
        tree_list_row = list_item.get_item()
        node_gobject = tree_list_row.get_item()
        label.set_text(node_gobject.display_text)

    def _load_dialogue_graphs(self):
        """Loads the dialogue graphs from the project manager."""
        self.model.remove_all()
        if self.project_manager.data.dialogue_graphs:
            self.active_graph = self.project_manager.data.dialogue_graphs[0]
        else:
            self.active_graph = LogicGraph(
                id="default_dialogue", name="Default Dialogue")
            self.project_manager.data.dialogue_graphs.append(self.active_graph)

        root_nodes = [
            n for n in self.active_graph.nodes if not n.inputs]
        for node in root_nodes:
            self.model.append(DialogueNodeGObject(node))

    def _on_add_dialogue_node(self, button):
        """Handles the clicked signal from the add dialogue button."""
        if not self.active_graph:
            return

        new_node_id = f"dnode_{len(self.active_graph.nodes)}"
        new_node = DialogueNode(
            id=new_node_id, node_type="Dialogue", character_id="char_01", dialogue_text="New dialogue...")

        selected_item = self.selection.get_selected_item()
        if selected_item:
            parent_node = selected_item.get_item().node
            parent_node.outputs.append(new_node_id)
            new_node.inputs.append(parent_node.id)

        self.active_graph.nodes.append(new_node)
        if not selected_item:
            self.model.append(DialogueNodeGObject(new_node))

        self.project_manager.set_dirty()
        self._load_dialogue_graphs()

    def _on_add_action_node(self, button):
        """Handles the clicked signal from the add action button."""
        if not self.active_graph:
            return

        selected_item = self.selection.get_selected_item()
        if not selected_item:
            return

        parent_node = selected_item.get_item().node
        if not isinstance(parent_node, DialogueNode):
            return

        new_node_id = f"anode_{len(self.active_graph.nodes)}"
        new_node = ActionNode(
            id=new_node_id, node_type="Action", action_command="SET_VARIABLE")

        parent_node.outputs.append(new_node_id)
        new_node.inputs.append(parent_node.id)

        self.active_graph.nodes.append(new_node)
        self.project_manager.set_dirty()
        self._load_dialogue_graphs()

    def _on_delete_node(self, button):
        """Handles the clicked signal from the delete button."""
        selected_item = self.selection.get_selected_item()
        if not selected_item or not self.active_graph:
            return

        node_to_delete = selected_item.get_item().node
        self.active_graph.nodes.remove(node_to_delete)

        self._load_dialogue_graphs()

        self.project_manager.set_dirty()

    def _on_selection_changed(self, selection, position, n_items):
        """Handles the selection-changed signal from the selection model."""
        selected_item = selection.get_selected_item()
        if selected_item:
            self.delete_button.set_sensitive(True)
            node_gobject = selected_item.get_item()
            self.dialogue_node_editor.set_node(node_gobject.node)
            self.properties_stack.set_visible_child_name("editor")
        else:
            self.delete_button.set_sensitive(False)
            self.properties_stack.set_visible_child_name("placeholder")
