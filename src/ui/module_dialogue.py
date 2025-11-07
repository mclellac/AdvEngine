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


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "module_dialogue.ui"))
class DialogueEditor(Adw.Bin):
    """A widget for editing dialogue trees."""
    __gtype_name__ = 'DialogueEditor'

    EDITOR_NAME = "Dialogue"
    VIEW_NAME = "dialogue_editor"
    ORDER = 3

    add_dialogue_button = Gtk.Template.Child()
    add_action_button = Gtk.Template.Child()
    delete_button = Gtk.Template.Child()
    dialogue_tree_view = Gtk.Template.Child()
    properties_stack = Gtk.Template.Child()
    dialogue_node_editor_placeholder = Gtk.Template.Child()

    def __init__(self, project_manager, settings_manager, **kwargs):
        """Initializes a new DialogueEditor instance."""
        print("DEBUG: DialogueEditor.__init__")
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.settings_manager = settings_manager
        self.active_graph = None

        self.dialogue_node_editor = DynamicNodeEditor(
            project_manager=self.project_manager, settings_manager=self.settings_manager, on_update_callback=self._on_node_updated)
        self.dialogue_node_editor_placeholder.append(self.dialogue_node_editor)

        self._setup_tree_view()
        self._connect_signals()
        self._load_dialogue_graphs()

    def _setup_tree_view(self):
        """Sets up the tree view and its model."""
        self.model = Gio.ListStore(item_type=DialogueNodeGObject)
        self.tree_model = Gtk.TreeListModel.new(
            self.model, passthrough=False, autoexpand=True, create_func=self._get_children)

        self.selection = Gtk.SingleSelection(model=self.tree_model)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._setup_list_item)
        factory.connect("bind", self._bind_list_item)
        factory.connect("unbind", self._unbind_list_item)

        self.dialogue_tree_view.set_model(self.selection)
        self.dialogue_tree_view.set_factory(factory)

    def _connect_signals(self):
        """Connects the widget signals to the handler functions."""
        self.add_dialogue_button.connect("clicked", self._on_add_dialogue_node)
        self.add_action_button.connect("clicked", self._on_add_action_node)
        self.delete_button.connect("clicked", self._on_delete_node)
        self.selection.connect("selection-changed", self._on_selection_changed)

    def _get_children(self, item, *args):
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
        if tree_list_row is None:
            return
        node_gobject = tree_list_row.get_item()
        if node_gobject:
            binding = node_gobject.bind_property("display_text", label, "label", GObject.BindingFlags.SYNC_CREATE)
            list_item.binding = binding

    def _unbind_list_item(self, factory, list_item):
        """Unbinds a list item from the data model."""
        if hasattr(list_item, 'binding'):
            list_item.binding.unbind()
            del list_item.binding

    def _load_dialogue_graphs(self):
        """Loads the dialogue graphs from the project manager."""
        print("DEBUG: DialogueEditor._load_dialogue_graphs")
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
        print("DEBUG: DialogueEditor._on_add_dialogue_node")
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
        # A bit of a hack to force the tree to update
        self.tree_model.set_model(Gio.ListStore(item_type=DialogueNodeGObject))
        self.tree_model.set_model(self.model)

    def _on_add_action_node(self, button):
        """Handles the clicked signal from the add action button."""
        print("DEBUG: DialogueEditor._on_add_action_node")
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
        # A bit of a hack to force the tree to update
        self.tree_model.set_model(Gio.ListStore(item_type=DialogueNodeGObject))
        self.tree_model.set_model(self.model)

    def _on_delete_node(self, button):
        """Handles the clicked signal from the delete button."""
        print("DEBUG: DialogueEditor._on_delete_node")
        selected_item = self.selection.get_selected_item()
        if not selected_item or not self.active_graph:
            return

        node_to_delete = selected_item.get_item().node
        self.active_graph.nodes.remove(node_to_delete)

        # Also remove from parent outputs
        for node in self.active_graph.nodes:
            if node_to_delete.id in node.outputs:
                node.outputs.remove(node_to_delete.id)

        self._load_dialogue_graphs()
        self.project_manager.set_dirty()

    def _on_selection_changed(self, selection, position, n_items):
        """Handles the selection-changed signal from the selection model."""
        print("DEBUG: DialogueEditor._on_selection_changed")
        selected_item = selection.get_selected_item()
        if selected_item:
            self.delete_button.set_sensitive(True)
            node_gobject = selected_item.get_item()
            self.dialogue_node_editor.set_node(node_gobject.node)
            self.properties_stack.set_visible_child_name("editor")
        else:
            self.delete_button.set_sensitive(False)
            self.properties_stack.set_visible_child_name("placeholder")

    def _on_node_updated(self):
        """Handles the node-updated signal from the dynamic node editor."""
        print("DEBUG: DialogueEditor._on_node_updated")
        selected_item = self.selection.get_selected_item()
        if selected_item:
            node_gobject = selected_item.get_item()
            node = node_gobject.node
            if isinstance(node, DialogueNode):
                node_gobject.display_text = f"{node.character_id}: {node.dialogue_text[:30]}..."
            elif isinstance(node, ActionNode):
                node_gobject.display_text = f"-> ACTION: {node.action_command}"

        # A bit of a hack to force the tree to update
        self.tree_model.set_model(Gio.ListStore(item_type=DialogueNodeGObject))
        self.tree_model.set_model(self.model)
