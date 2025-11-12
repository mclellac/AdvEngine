"""A dynamic property editor for logic nodes."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject
from ...core.ue_exporter import get_command_definitions

def pascal_to_snake(name):
    """Converts a PascalCase string to snake_case."""
    import re
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    return 'var_name' if name == 'varname' else name

class DynamicNodeEditor(Adw.Bin):
    """A dynamic property editor for a given node.

    This widget dynamically builds a UI to edit the properties of a LogicNode
    based on the command definitions in ue_exporter.py.

    Attributes:
        project_manager: The main project manager instance.
        settings_manager: The main settings manager instance.
        active_node (LogicNode): The currently active node being edited.
    """

    def __init__(self, **kwargs):
        """Initializes a new DynamicNodeEditor instance.

        Args:
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.project_manager = None
        self.settings_manager = None
        self.active_node = None
        self.on_update_callback = None
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_child(self.vbox)

    def set_managers(self, project_manager, settings_manager):
        """Sets the project and settings managers.

        Args:
            project_manager: The main project manager instance.
            settings_manager: The main settings manager instance.
        """
        self.project_manager = project_manager
        self.settings_manager = settings_manager

    def set_on_update_callback(self, callback):
        """Sets the callback function to be called when a value is updated.

        Args:
            callback: The function to call.
        """
        self.on_update_callback = callback

    def set_node(self, node):
        """Sets the active node and rebuilds the editor UI.

        Args:
            node (LogicNode): The node to edit.
        """
        self.active_node = node
        self._rebuild_ui()

    def _rebuild_ui(self):
        """Removes the old UI and creates a new one for the active node."""
        for child in self.vbox.get_children():
            self.vbox.remove(child)

        if not self.active_node:
            return

        group = Adw.PreferencesGroup()
        group.set_title(f"Properties: {self.active_node.id}")
        self.vbox.append(group)

        # Common properties
        id_row = Adw.EntryRow(title="ID", text=self.active_node.id)
        id_row.connect("notify::text", self.on_value_changed, "id")
        group.add(id_row)

        # Type-specific properties
        if self.active_node.node_type == "Dialogue":
            self._build_dialogue_ui(group)
        elif self.active_node.node_type == "Condition":
            self._build_condition_ui(group)
        elif self.active_node.node_type == "Action":
            self._build_action_ui(group)

    def _build_dialogue_ui(self, group):
        """Builds the UI for editing a DialogueNode.

        Args:
            group (Adw.PreferencesGroup): The group to add the UI to.
        """
        char_row = Adw.EntryRow(title="Character ID", text=self.active_node.character_id)
        char_row.connect("notify::text", self.on_value_changed, "character_id")
        group.add(char_row)

        text_row = Adw.EntryRow(title="Dialogue Text", text=self.active_node.dialogue_text)
        text_row.connect("notify::text", self.on_value_changed, "dialogue_text")
        group.add(text_row)

    def _build_condition_ui(self, group):
        """Builds the UI for editing a ConditionNode.

        Args:
            group (Adw.PreferencesGroup): The group to add the UI to.
        """
        defs = get_command_definitions()["conditions"]
        condition_types = list(defs.keys())

        type_row = Adw.ComboRow(title="Condition Type", model=Gtk.StringList.new(condition_types))
        type_row.set_selected(condition_types.index(self.active_node.condition_type))
        type_row.connect("notify::selected", self.on_condition_type_changed)
        group.add(type_row)

        self._build_params_ui(group, defs[self.active_node.condition_type]["params"])

    def _build_action_ui(self, group):
        """Builds the UI for editing an ActionNode.

        Args:
            group (Adw.PreferencesGroup): The group to add the UI to.
        """
        defs = get_command_definitions()["actions"]
        action_commands = list(defs.keys())

        command_row = Adw.ComboRow(title="Action Command", model=Gtk.StringList.new(action_commands))
        command_row.set_selected(action_commands.index(self.active_node.action_command))
        command_row.connect("notify::selected", self.on_action_command_changed)
        group.add(command_row)

        self._build_params_ui(group, defs[self.active_node.action_command]["params"])

    def _build_params_ui(self, group, params):
        """Builds the UI for a set of parameters.

        Args:
            group (Adw.PreferencesGroup): The group to add the UI to.
            params (dict): A dictionary of parameter names and their types.
        """
        for param, p_type in params.items():
            param_snake_case = pascal_to_snake(param)
            value = getattr(self.active_node, param_snake_case, "")

            if p_type == "str":
                row = Adw.EntryRow(title=param, text=str(value))
                row.connect("notify::text", self.on_value_changed, param_snake_case)
            elif p_type == "int":
                adjustment = Gtk.Adjustment(value=int(value), lower=0, upper=1000, step_increment=1)
                row = Adw.SpinRow(title=param, adjustment=adjustment)
                row.connect("notify::value", self.on_value_changed, param_snake_case)
            elif p_type == "bool":
                row = Adw.SwitchRow(title=param, active=bool(value))
                row.connect("notify::active", self.on_value_changed, param_snake_case)
            else:
                row = Adw.EntryRow(title=param, text=str(value))
                row.connect("notify::text", self.on_value_changed, param_snake_case)

            group.add(row)

    def on_value_changed(self, widget, prop, param_name):
        """Handles a value change in a property editor widget.

        Args:
            widget: The widget that emitted the signal.
            prop: The property that changed.
            param_name (str): The name of the parameter to update.
        """
        if isinstance(widget, Adw.EntryRow):
            new_value = widget.get_text()
        elif isinstance(widget, Adw.SpinRow):
            new_value = widget.get_value()
        elif isinstance(widget, Adw.SwitchRow):
            new_value = widget.get_active()
        else:
            return

        setattr(self.active_node, param_name, new_value)
        self.project_manager.set_dirty(True)
        if self.on_update_callback:
            self.on_update_callback()

    def on_condition_type_changed(self, combo_row, prop):
        """Handles a change in the condition type.

        Args:
            combo_row (Adw.ComboRow): The combo row for the condition type.
            prop: The property that changed.
        """
        self.active_node.condition_type = combo_row.get_selected_item().get_string()
        self._rebuild_ui()
        self.project_manager.set_dirty(True)

    def on_action_command_changed(self, combo_row, prop):
        """Handles a change in the action command.

        Args:
            combo_row (Adw.ComboRow): The combo row for the action command.
            prop: The property that changed.
        """
        self.active_node.action_command = combo_row.get_selected_item().get_string()
        self._rebuild_ui()
        self.project_manager.set_dirty(True)
