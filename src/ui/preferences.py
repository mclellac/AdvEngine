"""The preferences window for the AdvEngine application."""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject
from ..core.settings_manager import SettingsManager


class PreferencesDialog(Adw.PreferencesWindow):
    """A dialog for application and project preferences.

    This window provides a tabbed interface for managing various settings,
    including appearance, editor behavior, external tool paths, and project-
    specific options.
    """
    __gtype_name__ = "PreferencesDialog"

    def __init__(self, parent, project_manager=None, settings_manager=None):
        """Initializes a new PreferencesDialog instance.

        Args:
            parent: The parent window.
            project_manager: The project manager instance.
            settings_manager: The settings manager instance.
        """
        super().__init__(transient_for=parent, modal=True)
        self.project_manager = project_manager
        self.settings_manager = settings_manager

        self.set_search_enabled(False)
        self.set_title("Preferences")

        self._add_appearance_page()
        self._add_editor_page()
        self._add_tools_page()
        if self.project_manager:
            self._add_project_page()

    def _add_appearance_page(self):
        """Adds the Appearance page to the preferences window."""
        page = Adw.PreferencesPage()
        page.set_title("Appearance")
        page.set_icon_name("applications-graphics-symbolic")
        self.add(page)

        theme_group = Adw.PreferencesGroup(title="Theme")
        page.add(theme_group)

        style_manager = Adw.StyleManager.get_default()
        theme_row = Adw.ComboRow(
            title="Application Theme",
            subtitle="Choose how the application should look.",
            model=Gtk.StringList.new(["System", "Light", "Dark"])
        )
        theme_row.set_tooltip_text(
            "Set the application theme to match the system, or force light or dark mode.")
        theme_group.add(theme_row)

        if style_manager.get_dark():
            theme_row.set_selected(
                0 if style_manager.get_system_supports_color_schemes() else 2)
        else:
            theme_row.set_selected(1)
        theme_row.connect("notify::selected", self._on_theme_selected)

    def _add_tools_page(self):
        """Adds the External Tools page to the preferences window."""
        page = Adw.PreferencesPage()
        page.set_title("External Tools")
        page.set_icon_name("applications-utilities-symbolic")
        self.add(page)

        ue_group = Adw.PreferencesGroup(title="Unreal Engine")
        page.add(ue_group)

        ue_path_row = Adw.EntryRow(title="Editor Path")
        ue_path_row.set_text(self.settings_manager.get("ue_path", ""))
        ue_path_row.connect("changed", lambda entry: self.settings_manager.set("ue_path", entry.get_text()))
        ue_group.add(ue_path_row)

    def _add_project_page(self):
        """Adds the Project page to the preferences window."""
        page = Adw.PreferencesPage()
        page.set_title("Project")
        page.set_icon_name("folder-symbolic")
        self.add(page)

        project_group = Adw.PreferencesGroup(title="Project Settings")
        page.add(project_group)

        project_name_row = Adw.EntryRow(title="Project Name")
        project_name_row.set_tooltip_text("Set the name of the project.")
        project_name_row.set_text(
            self.settings_manager.get_project_setting("project_name"))
        project_name_row.connect("notify::text", self._on_project_name_changed)
        project_group.add(project_name_row)

        scene_names = [scene.name for scene in self.project_manager.data.scenes]
        scene_ids = [scene.id for scene in self.project_manager.data.scenes]

        default_scene_row = Adw.ComboRow(
            title="Default Starting Scene",
            model=Gtk.StringList.new(scene_names)
        )
        default_scene_row.set_tooltip_text(
            "Set the default scene that the game will load when it starts.")

        default_scene_id = self.settings_manager.get_project_setting(
            "default_scene")
        if default_scene_id in scene_ids:
            default_scene_row.set_selected(scene_ids.index(default_scene_id))

        default_scene_row.connect(
            "notify::selected", self._on_default_scene_changed, scene_ids)
        project_group.add(default_scene_row)

    def _on_theme_selected(self, combo_row, _):
        """Handles the theme selection."""
        style_manager = Adw.StyleManager.get_default()
        selected = combo_row.get_selected()
        if selected == 0:
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)
        elif selected == 1:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)

    def _on_project_name_changed(self, entry_row, _):
        """Handles the project name change."""
        self.settings_manager.set_project_setting(
            "project_name", entry_row.get_text())

    def _add_editor_page(self):
        """Adds the Editor page to the preferences window."""
        page = Adw.PreferencesPage()
        page.set_title("Editor")
        page.set_icon_name("document-edit-symbolic")
        self.add(page)

        # General Editor Settings
        general_group = Adw.PreferencesGroup(title="General")
        page.add(general_group)

        author_row = Adw.EntryRow(title="Default Author")
        author_row.set_text(self.settings_manager.get("author", ""))
        author_row.connect("changed", self._on_author_changed)
        general_group.add(author_row)

        # Autosave Settings
        autosave_group = Adw.PreferencesGroup(title="Autosave")
        page.add(autosave_group)

        autosave_row = Adw.SwitchRow(
            title="Enable Autosave",
            subtitle="Automatically save the project at a set interval."
        )
        autosave_row.set_tooltip_text(
            "If enabled, the project will be saved automatically every 5 minutes.")
        autosave_row.set_active(
            self.settings_manager.get_app_setting("autosave_enabled"))
        autosave_row.connect("notify::active", self._on_autosave_toggled)
        autosave_group.add(autosave_row)

        # Logic Editor Settings
        logic_editor_group = Adw.PreferencesGroup(title="Logic Editor")
        page.add(logic_editor_group)

        # Node Size
        default_node_width_row = Adw.SpinRow(
            title="Default Node Width",
            subtitle="The default width for new logic nodes.",
            adjustment=Gtk.Adjustment(value=240, lower=100, upper=500, step_increment=10),
        )
        default_node_width_row.set_value(self.settings_manager.get("default_node_width", 240))
        default_node_width_row.connect("notify::value", self._on_default_node_width_changed)
        logic_editor_group.add(default_node_width_row)

        default_node_height_row = Adw.SpinRow(
            title="Default Node Height",
            subtitle="The default height for new logic nodes.",
            adjustment=Gtk.Adjustment(value=160, lower=50, upper=400, step_increment=10),
        )
        default_node_height_row.set_value(self.settings_manager.get("default_node_height", 160))
        default_node_height_row.connect("notify::value", self._on_default_node_height_changed)
        logic_editor_group.add(default_node_height_row)

        # Grid Snapping
        grid_snapping_group = Adw.PreferencesGroup(title="Grid Snapping")
        page.add(grid_snapping_group)

        grid_snap_row = Adw.SwitchRow(
            title="Enable Grid Snapping",
            subtitle="Snap nodes and other elements to the grid."
        )
        grid_snap_row.set_active(self.settings_manager.get("grid_snap_enabled", True))
        grid_snap_row.connect("notify::active", self._on_grid_snap_toggled)
        grid_snapping_group.add(grid_snap_row)

        grid_size_row = Adw.SpinRow(
            title="Grid Size",
            subtitle="The size of the grid in pixels.",
            adjustment=Gtk.Adjustment(value=20, lower=5, upper=100, step_increment=5),
        )
        grid_size_row.set_value(self.settings_manager.get("grid_size", 20))
        grid_size_row.connect("notify::value", self._on_grid_size_changed)
        grid_snapping_group.add(grid_size_row)

    def _on_author_changed(self, entry):
        """Handles the changed signal from the author entry."""
        self.settings_manager.set("author", entry.get_text())

    def _on_default_node_width_changed(self, spin_row, _):
        """Handles the default node width change."""
        self.settings_manager.set("default_node_width", spin_row.get_value())

    def _on_default_node_height_changed(self, spin_row, _):
        """Handles the default node height change."""
        self.settings_manager.set("default_node_height", spin_row.get_value())

    def _on_grid_snap_toggled(self, switch, _):
        """Handles the grid snap toggle."""
        self.settings_manager.set("grid_snap_enabled", switch.get_active())

    def _on_grid_size_changed(self, spin_row, _):
        """Handles the grid size change."""
        self.settings_manager.set("grid_size", spin_row.get_value())

    def _on_default_scene_changed(self, combo_row, _, scene_ids):
        """Handles the default scene selection."""
        selected_index = combo_row.get_selected()
        if 0 <= selected_index < len(scene_ids):
            self.settings_manager.set_project_setting(
                "default_scene", scene_ids[selected_index])

    def _on_autosave_toggled(self, switch, _):
        """Handles the autosave toggle."""
        self.settings_manager.set_app_setting(
            "autosave_enabled", switch.get_active())
