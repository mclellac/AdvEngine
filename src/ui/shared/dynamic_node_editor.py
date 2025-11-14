"""A dynamic property editor for different types of logic nodes."""

import gi
import re

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from ...core.schemas.logic import ActionNode, ConditionNode, DialogueNode, LogicNode
from ...core.ue_exporter import get_command_definitions


def pascal_to_snake(name):
    """Converts a PascalCase string to snake_case.

    Args:
        name (str): The PascalCase string to convert.

    Returns:
        str: The converted snake_case string.
    """
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class DynamicNodeEditor(Adw.Bin):
    """A dynamic property editor for different types of logic nodes.

    This widget generates a user interface on-the-fly based on the properties
    of the currently selected logic node. It is used in both the LogicEditor
    and the DialogueEditor.

    Attributes:
        node (LogicNode): The currently selected node to be edited.
        project_manager: The main project manager instance.
        settings_manager: The main settings manager instance.
        on_update_callback (callable): A function to call when a node's data
            is updated.
    """

    __gtype_name__ = "DynamicNodeEditor"

    def __init__(
        self,
        **kwargs,
    ):
        """Initializes a new DynamicNodeEditor instance.

        Args:
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.node = None
        self.project_manager = None
        self.settings_manager = None
        self.on_update_callback = None
        self.main_widgets = {}
        self.param_widgets = {}

        self.container_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(self.container_box)

        self.main_group = None
        self.params_group = None

    def set_managers(self, project_manager, settings_manager):
        """Sets the project and settings managers.

        Args:
            project_manager: The project manager instance.
            settings_manager: The settings manager instance.
        """
        self.project_manager = project_manager
        self.settings_manager = settings_manager

    def set_on_update_callback(self, on_update_callback):
        """Sets the update callback.

        Args:
            on_update_callback (callable): The callback to be invoked.
        """
        self.on_update_callback = on_update_callback

    def set_node(self, node: LogicNode):
        """Sets the node to be edited and rebuilds the UI.

        Args:
            node (LogicNode): The node to edit.
        """
        self.node = node
        GLib.idle_add(self.build_ui)

    def build_ui(self) -> bool:
        """Builds the editor UI based on the current node's properties.

        Returns:
            bool: Always returns False to ensure the idle handler is removed.
        """
        if self.main_group:
            self.container_box.remove(self.main_group)
        if self.params_group:
            self.container_box.remove(self.params_group)

        self.main_widgets.clear()
        self.param_widgets.clear()

        self.main_group = Adw.PreferencesGroup()
        self.params_group = Adw.PreferencesGroup()
        self.container_box.append(self.main_group)
        self.container_box.append(self.params_group)

        if not self.node:
            self.params_group.set_visible(False)
            self.main_group.set_visible(False)
            return False

        self.main_group.set_visible(True)

        if isinstance(self.node, DialogueNode):
            self.add_entry(
                self.main_group, "character_id", "Character ID", self.node.character_id
            )
            self.add_entry(
                self.main_group,
                "dialogue_text",
                "Dialogue Text",
                self.node.dialogue_text,
            )
        elif isinstance(self.node, (ConditionNode, ActionNode)):
            defs = get_command_definitions()
            command_key = (
                "conditions" if isinstance(self.node, ConditionNode) else "actions"
            )
            command_type_key = (
                "condition_type"
                if isinstance(self.node, ConditionNode)
                else "action_command"
            )
            command_types = list(defs[command_key].keys())
            self.add_dropdown(
                self.main_group,
                command_type_key,
                "Type",
                command_types,
                getattr(self.node, command_type_key),
            )
            self.update_params_ui()
        return False

    def add_entry(self, group, key, title, default_value):
        """Adds an Adw.EntryRow to a preferences group.

        Args:
            group (Adw.PreferencesGroup): The group to add the row to.
            key (str): The property key associated with the entry.
            title (str): The display title for the entry row.
            default_value: The initial value for the entry.
        """
        entry = Adw.EntryRow(title=title)
        entry.set_text(str(default_value))
        entry.connect("notify::text", self.on_value_changed)
        self.main_widgets[key] = entry
        group.add(entry)

    def add_dropdown(self, group, key, title, options, default_value):
        """Adds an Adw.ComboRow to a preferences group.

        Args:
            group (Adw.PreferencesGroup): The group to add the row to.
            key (str): The property key associated with the dropdown.
            title (str): The display title for the combo row.
            options (list[str]): The list of options for the dropdown.
            default_value: The initial selected value.
        """
        combo = Adw.ComboRow(title=title, model=Gtk.StringList.new(options))
        if default_value in options:
            combo.set_selected(options.index(default_value))
        combo.connect("notify::selected-item", self.on_combo_changed)
        self.main_widgets[key] = combo
        group.add(combo)

    def update_params_ui(self, *args):
        """Updates the parameters UI section based on the selected command."""
        if self.params_group:
            self.container_box.remove(self.params_group)
        self.param_widgets.clear()

        self.params_group = Adw.PreferencesGroup()
        self.container_box.append(self.params_group)

        if not isinstance(self.node, (ConditionNode, ActionNode)):
            self.params_group.set_visible(False)
            return

        self.params_group.set_visible(True)
        command_key = (
            "conditions" if isinstance(self.node, ConditionNode) else "actions"
        )
        command_type_key = (
            "condition_type"
            if isinstance(self.node, ConditionNode)
            else "action_command"
        )
        selected_command = (
            self.main_widgets[command_type_key].get_selected_item().get_string()
        )

        if selected_command:
            defs = get_command_definitions()[command_key][selected_command]
            self.params_group.set_title(f"Parameters for {selected_command}")
            for param, p_type in defs["params"].items():
                self.add_param_widget(
                    param, p_type, getattr(self.node, pascal_to_snake(param), "")
                )

    def add_param_widget(self, key, param_type, default_value):
        """Adds a widget for a command parameter.

        Args:
            key (str): The parameter key.
            param_type (str or list): The type of the parameter.
            default_value: The initial value for the parameter.
        """
        snake_key = pascal_to_snake(key)
        title = key.replace("_", " ").title()

        if isinstance(param_type, list):
            widget = Adw.ComboRow(title=title, model=Gtk.StringList.new(param_type))
            if default_value in param_type:
                widget.set_selected(param_type.index(default_value))
            widget.connect("notify::selected-item", self.on_value_changed)
        elif param_type == "bool":
            widget = Gtk.CheckButton(label=title)
            widget.set_active(bool(default_value))
            widget.connect("toggled", self.on_value_changed)
        elif param_type == "int":
            widget = Gtk.SpinButton(
                adjustment=Gtk.Adjustment(lower=0, upper=999999, step_increment=1)
            )
            widget.set_value(int(default_value or 0))
            widget.connect("value-changed", self.on_value_changed)
        else:
            widget = Adw.EntryRow(title=title)
            widget.set_text(str(default_value))
            widget.connect("notify::text", self.on_value_changed)

        self.param_widgets[snake_key] = widget
        if not isinstance(widget, Gtk.CheckButton):
            self.params_group.add(widget)
        else:
            row = Adw.ActionRow(title=title, activatable_widget=widget)
            row.add_suffix(widget)
            self.params_group.add(row)

    def on_combo_changed(self, combo, _):
        """Handles the changed signal from a combo box.

        Args:
            combo (Adw.ComboRow): The combo row that emitted the signal.
            _: Unused parameter.
        """
        self.on_value_changed(combo)
        self.update_params_ui()

    def on_value_changed(self, widget, *args):
        """Handles value changes from any widget in the editor.

        Args:
            widget: The widget that emitted the signal.
            *args: Additional arguments from the signal.
        """
        if not self.node:
            return

        values = self.get_values()
        for key, value in values.items():
            if hasattr(self.node, key):
                field_type = getattr(self.node.__class__, "__annotations__", {}).get(
                    key, "any"
                )

                coerced_value = value
                if field_type == int:
                    try:
                        coerced_value = int(value)
                    except (ValueError, TypeError):
                        coerced_value = 0
                elif field_type == bool:
                    coerced_value = str(value).lower() in ["true", "1", "yes"]
                elif field_type == str:
                    coerced_value = str(value)

                setattr(self.node, key, coerced_value)

        if self.project_manager:
            self.project_manager.set_dirty(True)
        if self.on_update_callback:
            self.on_update_callback()

    def get_values(self) -> dict:
        """Gets all values from the editor widgets.

        Returns:
            dict: A dictionary of property keys and their current values.
        """
        values = {}
        all_widgets = {**self.main_widgets, **self.param_widgets}

        for key, widget in all_widgets.items():
            value = None
            if isinstance(widget, Adw.EntryRow):
                value = widget.get_text()
            elif isinstance(widget, Adw.ComboRow):
                selected_item = widget.get_selected_item()
                if selected_item:
                    value = selected_item.get_string()
            elif isinstance(widget, Gtk.CheckButton):
                value = widget.get_active()
            elif isinstance(widget, Gtk.SpinButton):
                value = widget.get_value_as_int()

            if value is not None:
                values[key] = value
        return values
