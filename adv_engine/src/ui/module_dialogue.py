import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from ..core.data_schemas import DialogueNode, LogicGraph

class DialogueNodeEditor(Gtk.Box):
    def __init__(self, node: DialogueNode, project_manager):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.node = node
        self.project_manager = project_manager
        self.tree_view_model = None
        self.tree_iter = None

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.append(Gtk.Label(label="Character ID:", halign=Gtk.Align.START))
        self.character_id_entry = Gtk.Entry(text=self.node.character_id if self.node else "")
        self.append(self.character_id_entry)

        self.append(Gtk.Label(label="Dialogue Text:", halign=Gtk.Align.START))
        self.dialogue_text_view = Gtk.TextView()
        self.dialogue_text_view.get_buffer().set_text(self.node.dialogue_text if self.node else "")
        self.dialogue_text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.dialogue_text_view.set_size_request(-1, 100)
        scrollable_textview = Gtk.ScrolledWindow()
        scrollable_textview.set_child(self.dialogue_text_view)
        scrollable_textview.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.append(scrollable_textview)

        save_button = Gtk.Button(label="Save Changes")
        save_button.connect("clicked", self.on_save_clicked)
        self.append(save_button)

    def on_save_clicked(self, button):
        if self.node:
            self.node.character_id = self.character_id_entry.get_text()
            buffer = self.dialogue_text_view.get_buffer()
            start_iter, end_iter = buffer.get_bounds()
            self.node.dialogue_text = buffer.get_text(start_iter, end_iter, False)
            self.project_manager.set_dirty()

            # Update the text in the tree view
            if self.tree_view_model and self.tree_iter:
                display_text = f"{self.node.character_id}: {self.node.dialogue_text[:30]}..."
                self.tree_view_model.set_value(self.tree_iter, 1, display_text)

    def update_node(self, node, model, tree_iter):
        """Update the editor to show a new node's properties."""
        self.node = node
        self.tree_view_model = model
        self.tree_iter = tree_iter
        self.character_id_entry.set_text(self.node.character_id)
        self.dialogue_text_view.get_buffer().set_text(self.node.dialogue_text)

class DialogueEditor(Gtk.Box):
    def __init__(self, project_manager):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.project_manager = project_manager
        self.active_graph = None
        self.node_editor = None

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.append(paned)

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        paned.set_start_child(left_box)

        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        left_box.append(toolbar)

        add_button = Gtk.Button(label="Add")
        add_button.connect("clicked", self.on_add_node)
        toolbar.append(add_button)

        self.delete_button = Gtk.Button(label="Delete")
        self.delete_button.set_sensitive(False)
        self.delete_button.connect("clicked", self.on_delete_node)
        toolbar.append(self.delete_button)

        tree_view_scrolled_window = Gtk.ScrolledWindow()
        tree_view_scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        tree_view_scrolled_window.set_hexpand(True)
        tree_view_scrolled_window.set_vexpand(True)
        left_box.append(tree_view_scrolled_window)

        self.tree_store = Gtk.TreeStore(str, str)  # Node ID, Display Text
        self.tree_view = Gtk.TreeView(model=self.tree_store)
        tree_view_scrolled_window.set_child(self.tree_view)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Dialogue Flow", renderer, text=1)
        self.tree_view.append_column(column)

        properties_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        properties_box.set_size_request(350, -1)
        paned.set_end_child(properties_box)

        self.properties_stack = Gtk.Stack()
        self.properties_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        properties_box.append(self.properties_stack)

        placeholder_label = Gtk.Label(label="Select a node to edit its properties.")
        self.properties_stack.add_named(placeholder_label, "placeholder")
        self.properties_stack.set_visible_child_name("placeholder")

        self.tree_view.get_selection().connect("changed", self.on_tree_selection_changed)
        self._load_dialogue_graphs()

    def on_add_node(self, button):
        if not self.active_graph:
            return

        selection = self.tree_view.get_selection()
        model, parent_iter = selection.get_selected()

        parent_node = None
        if parent_iter:
            parent_id = model[parent_iter][0]
            parent_node = next((n for n in self.active_graph.nodes if n.id == parent_id), None)

        new_node_id = f"dnode_{len(self.active_graph.nodes)}"
        new_node = DialogueNode(
            id=new_node_id,
            node_type="Dialogue",
            character_id="char_01",
            dialogue_text="New dialogue...",
            x=0, y=0 # Position is not used in the tree view
        )

        if parent_node:
            new_node.inputs.append(parent_node.id)
            parent_node.outputs.append(new_node.id)

        self.active_graph.nodes.append(new_node)
        self.project_manager.set_dirty()

        # Add to tree view
        display_text = f"{new_node.character_id}: {new_node.dialogue_text[:30]}..."
        new_iter = self.tree_store.append(parent_iter, [new_node.id, display_text])

        # Auto-select the new node
        self.tree_view.get_selection().select_iter(new_iter)


    def on_delete_node(self, button):
        selection = self.tree_view.get_selection()
        model, tree_iter = selection.get_selected()

        if not tree_iter or not self.active_graph:
            return

        node_id = model[tree_iter][0]
        node_to_delete = next((n for n in self.active_graph.nodes if n.id == node_id), None)

        if node_to_delete:
            # Remove connections
            for parent_id in node_to_delete.inputs:
                parent_node = next((n for n in self.active_graph.nodes if n.id == parent_id), None)
                if parent_node and node_id in parent_node.outputs:
                    parent_node.outputs.remove(node_id)

            # For simplicity, this example doesn't reconnect children.
            # A real implementation would need to handle orphaned nodes.

            # Remove the node itself
            self.active_graph.nodes.remove(node_to_delete)
            self.project_manager.set_dirty()

            # Remove from tree view
            self.tree_store.remove(tree_iter)

    def _load_dialogue_graphs(self):
        self.tree_store.clear()
        if self.project_manager.data.dialogue_graphs:
            self.active_graph = self.project_manager.data.dialogue_graphs[0]
        else:
            self.active_graph = LogicGraph(id="default_dialogue", name="Default Dialogue")
            self.project_manager.data.dialogue_graphs.append(self.active_graph)

        # Find the root node (a node with no inputs)
        root_nodes = [n for n in self.active_graph.nodes if not n.inputs]
        if root_nodes:
            # Let's assume the first root node is the start of the dialogue
            self._populate_tree(root_nodes[0], None)

    def _populate_tree(self, node, parent_iter):
        if isinstance(node, DialogueNode):
            display_text = f"{node.character_id}: {node.dialogue_text[:30]}..."
            current_iter = self.tree_store.append(parent_iter, [node.id, display_text])

            # Recurse through children
            for child_id in node.outputs:
                child_node = next((n for n in self.active_graph.nodes if n.id == child_id), None)
                if child_node:
                    self._populate_tree(child_node, current_iter)

    def on_tree_selection_changed(self, selection):
        model, tree_iter = selection.get_selected()
        if tree_iter:
            self.delete_button.set_sensitive(True)
            node_id = model[tree_iter][0]

            node = next((n for n in self.active_graph.nodes if n.id == node_id), None)

            if node and isinstance(node, DialogueNode):
                if not self.node_editor:
                    self.node_editor = DialogueNodeEditor(node, self.project_manager)
                    self.properties_stack.add_named(self.node_editor, "editor")
                else:
                    self.node_editor.update_node(node, model, tree_iter)

                self.properties_stack.set_visible_child_name("editor")
            else:
                self.properties_stack.set_visible_child_name("placeholder")
        else:
            self.delete_button.set_sensitive(False)
            self.properties_stack.set_visible_child_name("placeholder")
